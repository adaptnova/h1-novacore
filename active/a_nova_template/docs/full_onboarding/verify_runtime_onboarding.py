#!/usr/bin/env python3
"""Runtime verifier for full Nova onboarding.

Creates a temp Nova unless --nova-home is supplied, exercises realtime plugin
pre/post hooks, validates MemFirst fanout, probes available infra, writes an
E2E trace, verifies playback, and inventories Temporal.io touch points.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = Path('/adapt/novas/active/a_nova_template')
SECRETS = [Path('/adapt/secrets/db.env'), Path('/adapt/secrets/m2.env')]

SECRET_KEY_RE = re.compile(r'(KEY|TOKEN|SECRET|PASSWORD|PASS|AUTH|CREDENTIAL)', re.I)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def redact_value(key: str, value: str) -> str:
    if SECRET_KEY_RE.search(key):
        return '<set>' if value else ''
    if '://' in value and '@' in value:
        return re.sub(r'//([^/@:]+):([^/@]+)@', r'//\1:<redacted>@', value)
    return value


def load_env_file(path: Path) -> dict[str, str]:
    loaded: dict[str, str] = {}
    if not path.exists():
        return loaded
    for raw in path.read_text(errors='ignore').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        if line.startswith('export '):
            line = line[7:].strip()
        k, v = line.split('=', 1)
        k = k.strip()
        v = v.strip().strip('"\'')
        if k and k not in os.environ:
            os.environ[k] = v
        if k:
            loaded[k] = redact_value(k, v)
    return loaded


def run(cmd: list[str], timeout: int = 20, input_text: str | None = None) -> dict[str, Any]:
    try:
        proc = subprocess.run(cmd, input=input_text, text=True, capture_output=True, timeout=timeout)
        return {
            'ok': proc.returncode == 0,
            'code': proc.returncode,
            'stdout': proc.stdout[-1200:],
            'stderr': proc.stderr[-1200:],
        }
    except Exception as exc:
        return {'ok': False, 'code': -1, 'stderr': str(exc)}


def create_temp_nova(name: str) -> tuple[Path, Path, dict[str, Any]]:
    base = Path(tempfile.mkdtemp(prefix='nova_runtime_onboard_base_', dir='/data/vast/tmp' if Path('/data/vast/tmp').exists() else None))
    profiles = Path(tempfile.mkdtemp(prefix='nova_runtime_onboard_profiles_', dir='/data/vast/tmp' if Path('/data/vast/tmp').exists() else None))
    cmd = [sys.executable, str(TEMPLATE / 'nova.py'), '--name', name, '--base-dir', str(base), '--profiles-dir', str(profiles), '--skip-hermes-register', '--validate']
    created = run(cmd, timeout=120)
    return base / name, profiles, {'base': str(base), 'profiles': str(profiles), 'create': created}


def load_plugin(home: Path, profile: str) -> tuple[Any, dict[str, str]]:
    plugin_path = home / 'plugins/memfirst-realtime/__init__.py'
    env = {'NOVA_HOME': str(home), 'NOVA_PROFILE': profile, 'HERMES_HOME': str(home)}
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    spec = importlib.util.spec_from_file_location('memfirst_realtime_probe', plugin_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'cannot load plugin {plugin_path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    for k, v in old.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    return module, env


def probe_hooks(home: Path, profile: str, session_id: str) -> dict[str, Any]:
    module, env = load_plugin(home, profile)
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    try:
        pre = module._on_pre_llm_call(user_message='runtime verifier pre hook probe', session_id=session_id)  # type: ignore[attr-defined]
        module._on_post_llm_call(
            session_id=session_id,
            user_message='runtime verifier user probe',
            assistant_response='runtime verifier assistant probe',
            platform='runtime_verifier',
        )
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    l0 = home / 'memory/l0/intake/sessions' / f'{session_id}.jsonl'
    root = home / 'sessions' / f'{session_id}.jsonl'
    l5 = list((home / 'memory/l5/raw').glob(f'session-{session_id}-*.json')) if (home / 'memory/l5/raw').exists() else []
    return {
        'pre_llm_call': {
            'ok': isinstance(pre, dict) and bool(pre.get('context')) and '<MemFirst realtime context>' in pre.get('context', ''),
            'context_bytes': len(pre.get('context', '')) if isinstance(pre, dict) else 0,
        },
        'post_llm_call': {
            'l0': {'ok': l0.exists(), 'path': str(l0)},
            'sessions': {'ok': root.exists(), 'path': str(root)},
            'l5_raw': {'ok': bool(l5), 'paths': [str(p) for p in l5[:3]]},
        },
    }


def run_ingest_direct(home: Path, profile: str, session_id: str) -> dict[str, Any]:
    cmd = [
        sys.executable, str(home / 'scripts/memfirst_ingest.py'),
        '--nova-home', str(home), '--profile', profile, '--session-id', session_id,
        '--user-message', 'direct runtime ingest user probe',
        '--assistant-response', 'direct runtime ingest assistant probe',
        '--source', 'runtime_verifier_direct',
    ]
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=90)
        out = {'ok': proc.returncode == 0, 'code': proc.returncode, 'stdout_tail': proc.stdout[-1200:], 'stderr_tail': proc.stderr[-1200:]}
        parsed = json.loads(proc.stdout) if proc.stdout.strip() else None
    except Exception as exc:
        out = {'ok': False, 'code': -1, 'stderr_tail': str(exc)}
        parsed = {'parse_error': str(exc)}
    return {'process': out, 'parsed': parsed}


def probe_nats(profile: str, trace_id: str) -> dict[str, Any]:
    if not shutil.which('nats'):
        return {'ok': False, 'skipped': True, 'reason': 'nats CLI missing'}
    url = os.environ.get('NATS_URL') or 'nats://localhost:18020'
    cmd = ['nats', '--server', url]
    if os.environ.get('NATS_USER'):
        cmd += ['--user', os.environ['NATS_USER']]
    if os.environ.get('NATS_PASSWORD'):
        cmd += ['--password', os.environ['NATS_PASSWORD']]
    conn = run(cmd + ['server', 'check', 'connection'], timeout=10)
    pub = run(cmd + ['pub', f'trace.{profile}.e2e', json.dumps({'trace_id': trace_id, 'profile': profile})], timeout=10)
    return {'ok': conn['ok'] and pub['ok'], 'connection': conn, 'publish_trace': pub, 'subjects': [f'nova.{profile}.direct', f'nova.{profile}.events', f'memory.{profile}.session_turn', f'trace.{profile}.e2e']}


def probe_dragonfly(profile: str, trace_id: str) -> dict[str, Any]:
    if not shutil.which('redis-cli'):
        return {'ok': False, 'skipped': True, 'reason': 'redis-cli missing'}
    key = f'nova:{profile}:heartbeat:{trace_id}'
    if os.environ.get('DRAGONFLY_URL'):
        base = ['redis-cli', '-u', os.environ['DRAGONFLY_URL']]
    else:
        base = ['redis-cli', '-h', '127.0.0.1', '-p', os.environ.get('DRAGONFLY_PORT', '18000')]
        password = os.environ.get('DRAGONFLY_PASSWORD') or os.environ.get('REDIS_PASSWORD') or os.environ.get('NATS_PASSWORD')
        if password:
            base += ['-a', password, '--no-auth-warning']
    ping = run(base + ['ping'], timeout=10)
    setr = run(base + ['setex', key, '60', now()], timeout=10) if ping['ok'] else {'ok': False, 'skipped': True, 'reason': 'ping failed'}
    getr = run(base + ['get', key], timeout=10) if setr.get('ok') else {'ok': False, 'skipped': True, 'reason': 'set failed'}
    delr = run(base + ['del', key], timeout=10) if setr.get('ok') else {'ok': False, 'skipped': True, 'reason': 'set failed'}
    return {'ok': bool(ping['ok'] and setr.get('ok') and getr.get('ok')), 'ping': ping, 'setex': setr, 'get': getr, 'delete': delr, 'namespace_probe': key}


def probe_redpanda(profile: str, trace_id: str) -> dict[str, Any]:
    if not shutil.which('rpk'):
        return {'ok': False, 'skipped': True, 'reason': 'rpk missing'}
    brokers = os.environ.get('REDPANDA_BROKERS') or '127.0.0.1:18021'
    info = run(['rpk', 'cluster', 'info', '--brokers', brokers], timeout=15)
    topics = run(['rpk', 'topic', 'list', '--brokers', brokers], timeout=15) if info['ok'] else {'ok': False, 'skipped': True, 'reason': 'cluster info failed'}
    expected = ['nova.session_turns', 'nova.memory_mutations', 'nova.lifecycle', 'nexus.messages', 'trace.e2e']
    present = []
    if topics.get('stdout'):
        present = [t for t in expected if t in topics['stdout']]
    return {'ok': bool(info['ok'] and not [t for t in expected if t not in present]), 'cluster': info, 'topics': topics, 'expected_topics': expected, 'present_topics': present, 'missing_topics': [t for t in expected if t not in present]}


def probe_nebula(profile: str) -> dict[str, Any]:
    cli = shutil.which('nebula-console') or shutil.which('ngql')
    if not cli:
        return {'ok': False, 'skipped': True, 'reason': 'NebulaDB CLI missing (nebula-console/ngql)'}
    # Do not guess credentials. Inventory command availability only unless env gives explicit command.
    return {'ok': False, 'skipped': True, 'reason': 'NebulaDB CLI present but no safe credential/env contract implemented', 'cli': cli, 'expected_spaces': ['novaops', 'memfirst'], 'profile_vertex': profile}


def probe_vector(home: Path, ingest: dict[str, Any]) -> dict[str, Any]:
    parsed = ingest.get('parsed') or {}
    l3 = ((parsed.get('layers') or {}).get('l3') or {}) if isinstance(parsed, dict) else {}
    db = home / 'memory/l3/data/shared'
    return {'ok': bool(l3.get('ok')), 'l3_result': l3, 'index_path_exists': db.exists(), 'index_path': str(db)}


def probe_hermes_databases(home: Path) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for name in ['state.db', 'response_store.db']:
        p = home / name
        item = {'exists': p.exists(), 'path': str(p)}
        if p.exists():
            try:
                con = sqlite3.connect(f'file:{p}?mode=ro', uri=True)
                con.execute('select 1').fetchone()
                con.close()
                item['ok'] = True
            except Exception as exc:
                item['ok'] = False
                item['error'] = str(exc)
        else:
            item['ok'] = True if name == 'response_store.db' else False
            item['skipped'] = name == 'response_store.db'
        results[name] = item
    locks = [str(p) for p in [home / '.lock', home / 'state.db.lock'] if p.exists()]
    sessions = list((home / 'sessions').glob('*.jsonl')) if (home / 'sessions').exists() else []
    return {'ok': bool(sessions) and not locks, 'dbs': results, 'sessions_count': len(sessions), 'stale_locks': locks}


def _probe_status(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        if 'ok' in value or 'skipped' in value:
            return {'ok': value.get('ok'), 'skipped': value.get('skipped', False), 'reason': value.get('reason', '')}
        if 'parsed' in value and isinstance(value.get('parsed'), dict):
            return {'ok': value['parsed'].get('ok'), 'skipped': False, 'reason': ''}
        if 'pre_llm_call' in value:
            return {'ok': bool(value.get('pre_llm_call', {}).get('ok')), 'skipped': False, 'reason': ''}
    return {'ok': None, 'skipped': False, 'reason': ''}


def write_trace(home: Path, profile: str, trace_id: str, session_id: str, report: dict[str, Any]) -> dict[str, Any]:
    layer_summary = {name: _probe_status(value) for name, value in (report.get('probes') or {}).items()}
    event = {
        'trace_id': trace_id,
        'correlation_id': f'corr-{trace_id}',
        'session_id': session_id,
        'turn_id': f'turn-{trace_id}',
        'profile': profile,
        'source_surface': 'runtime_verifier',
        'target_surface': 'hermes_plugin_memfirst',
        'route': f'runtime_verifier->{profile}->memfirst',
        'model_provider': 'not_called_runtime_probe',
        'model_name': 'not_called_runtime_probe',
        'user_message_hash': 'probe-user',
        'assistant_response_hash': 'probe-assistant',
        'timestamps': {'received_at': now(), 'fanout_complete_at': now()},
        'layer_results': layer_summary,
    }
    log = home / 'memory/l0/intake/logs/trace.e2e.jsonl'
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text((log.read_text() if log.exists() else '') + json.dumps(event, ensure_ascii=False) + '\n', encoding='utf-8')
    raw = home / 'memory/l5/raw' / f'trace-{trace_id}.json'
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_text(json.dumps(event, indent=2, ensure_ascii=False), encoding='utf-8')
    return {'ok': log.exists() and raw.exists(), 'local_jsonl': str(log), 'l5_raw': str(raw), 'event': event}


def playback_trace(trace: dict[str, Any]) -> dict[str, Any]:
    required = ['trace_id', 'correlation_id', 'session_id', 'turn_id', 'profile', 'source_surface', 'target_surface', 'route', 'timestamps', 'layer_results']
    missing = [k for k in required if k not in trace.get('event', {})]
    broken = []
    layers = trace.get('event', {}).get('layer_results', {})
    for name, value in layers.items():
        if isinstance(value, dict) and value.get('ok') is False and not value.get('skipped'):
            broken.append(name)
    return {'ok': not missing, 'missing_fields': missing, 'first_broken_hop': broken[0] if broken else None, 'reconstructed_route': trace.get('event', {}).get('route')}


def temporal_inventory() -> dict[str, Any]:
    temporal_cli = shutil.which('temporal')
    tctl = shutil.which('tctl')
    services_user = run(['bash', '-lc', "systemctl --user list-units --type=service --all --no-pager | grep -i temporal || true"], timeout=20)
    services_system = run(['bash', '-lc', "systemctl list-units --type=service --all --no-pager 2>/dev/null | grep -i temporal || true"], timeout=20)
    processes = run(['bash', '-lc', "pgrep -af temporal | grep -v 'grep' | grep -v 'verify_runtime_onboarding' | grep -v 'runtime_onboarding_report' | grep -v 'hermes-snap' | head -80 || true"], timeout=20)
    ports = run(['bash', '-lc', "ss -ltnp 2>/dev/null | grep -E '(:7233|:8233|temporal)' || true"], timeout=20)
    cli_status = run([temporal_cli, 'operator', 'cluster', 'health'], timeout=10) if temporal_cli else {'ok': False, 'skipped': True, 'reason': 'temporal CLI missing'}
    namespaces = run([temporal_cli, 'operator', 'namespace', 'list'], timeout=10) if temporal_cli else {'ok': False, 'skipped': True, 'reason': 'temporal CLI missing'}
    known_paths = [
        '/adapt/platform/timeops',
        '/adapt/platform/timeops/tier2/pmops',
        '/adapt/platform/orchops',
        '/adapt/platform/dataops/dbops/integrations/temporal_langgraph_bridge.py',
        '/adapt/novas/temporal_nova_core',
        '/adapt/platform/novaops/toolops/mcp_servers/temporal-mcp',
        '/adapt/projects/mem/tests/test_temporal_workflows.py',
    ]
    path_hits = []
    for raw in known_paths:
        p = Path(raw)
        if p.exists():
            path_hits.append(str(p))
    return {
        'ok': bool((processes.get('stdout') or '').strip() or cli_status.get('ok')),
        'temporal_cli': temporal_cli,
        'tctl': tctl,
        'services_user': services_user,
        'services_system': services_system,
        'processes': processes,
        'ports_7233_8233': ports,
        'cluster_health': cli_status,
        'namespaces': namespaces,
        'known_touch_paths': path_hits,
        'summary': 'Temporal touches are inventory-only here: services/processes/ports/CLI/namespaces/known repos. No workflow mutation is performed.',
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Verify runtime full Nova onboarding')
    parser.add_argument('--nova-home', default='')
    parser.add_argument('--profile', default='')
    parser.add_argument('--name', default='RuntimeOnboardProbe')
    parser.add_argument('--keep-temp', action='store_true')
    args = parser.parse_args(argv)

    env_loaded = {str(p): load_env_file(p) for p in SECRETS}
    created: dict[str, Any] | None = None
    if args.nova_home:
        home = Path(args.nova_home).expanduser().resolve()
        profiles = None
    else:
        home, profiles, created = create_temp_nova(args.name)
    profile = args.profile or home.name.lower().replace('_', '-')
    trace_id = uuid.uuid4().hex[:12]
    hook_session = f'runtime-hook-{trace_id}'
    direct_session = f'runtime-direct-{trace_id}'

    report: dict[str, Any] = {
        'ok': False,
        'home': str(home),
        'profile': profile,
        'created_temp': created,
        'env_loaded_redacted': env_loaded,
        'trace_id': trace_id,
        'probes': {},
    }

    probes = report['probes']
    probes['hooks'] = probe_hooks(home, profile, hook_session)
    ingest = run_ingest_direct(home, profile, direct_session)
    probes['direct_ingest'] = ingest
    probes['nats'] = probe_nats(profile, trace_id)
    probes['dragonflydb'] = probe_dragonfly(profile, trace_id)
    probes['redpanda'] = probe_redpanda(profile, trace_id)
    probes['nebuladb'] = probe_nebula(profile)
    probes['vector_db'] = probe_vector(home, ingest)
    probes['hermes_databases'] = probe_hermes_databases(home)
    probes['temporal_io_touch_inventory'] = temporal_inventory()
    trace = write_trace(home, profile, trace_id, direct_session, report)
    probes['e2e_trace'] = trace
    probes['playback'] = playback_trace(trace)

    critical = [
        probes['hooks']['pre_llm_call']['ok'],
        probes['hooks']['post_llm_call']['l0']['ok'],
        probes['hooks']['post_llm_call']['sessions']['ok'],
        bool((ingest.get('parsed') or {}).get('ok')),
        probes['e2e_trace']['ok'],
        probes['playback']['ok'],
    ]
    layer_results = ((ingest.get('parsed') or {}).get('layers') or {}) if isinstance(ingest.get('parsed'), dict) else {}
    production_required = {
        'l0': bool((layer_results.get('l0') or {}).get('ok')),
        'sessions': bool((layer_results.get('sessions') or {}).get('ok')),
        'l3': bool((layer_results.get('l3') or {}).get('ok')),
        'l4': bool((layer_results.get('l4') or {}).get('ok')),
        'l5': bool((layer_results.get('l5') or {}).get('ok')),
        'l6': bool((layer_results.get('l6') or {}).get('ok')),
        'nats': bool(probes['nats'].get('ok')),
        'dragonflydb': bool(probes['dragonflydb'].get('ok')),
        'redpanda_topics': bool(probes['redpanda'].get('ok')),
        'vector_db': bool(probes['vector_db'].get('ok')),
        'e2e_trace': bool(probes['e2e_trace'].get('ok')),
        'playback': bool(probes['playback'].get('ok')),
        'temporal_io_touch_inventory': bool(probes['temporal_io_touch_inventory'].get('ok')),
    }
    report['runtime_probe_ok'] = all(critical)
    report['production_gate_ok'] = all(production_required.values())
    report['production_required'] = production_required
    report['ok'] = report['runtime_probe_ok']
    report['temp_cleanup'] = 'kept' if args.keep_temp or args.nova_home else 'removed'
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if created and not args.keep_temp:
        try:
            shutil.rmtree(Path(created['base']))
            shutil.rmtree(Path(created['profiles']))
        except Exception:
            pass
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
