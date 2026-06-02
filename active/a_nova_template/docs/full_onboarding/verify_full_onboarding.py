#!/usr/bin/env python3
"""Static verifier for full Nova + Hermes onboarding."""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


def check_jsonl(path: Path) -> bool:
    try:
        for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
            if line.strip():
                json.loads(line)
        return True
    except Exception:
        return False


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print('usage: verify_full_onboarding.py /adapt/novas/active/<Name>')
        return 2
    home = Path(argv[1]).expanduser().resolve()
    profile = home.name.lower().replace('_', '-')
    results: dict[str, object] = {'home': str(home), 'profile_guess': profile, 'checks': {}}
    checks: dict[str, object] = results['checks']  # type: ignore[assignment]

    required_files = [
        'SOUL.md', 'MEMORY.md', 'USER.md', 'config.yaml', '.env',
        'memory/l1/SOUL.md', 'memory/l1/MEMORY.md', 'memory/l1/USER.md',
        'plugins/memfirst-realtime/plugin.yaml', 'plugins/memfirst-realtime/__init__.py',
        'scripts/memfirst_ingest.py',
    ]
    required_dirs = [
        'memory/l0/intake/sessions', 'sessions', 'memory/l2', 'memory/l3/data',
        'memory/l4/data', 'memory/l5', 'memory/l6/data', 'plugins', 'scripts',
    ]

    checks['required_files'] = {rel: (home / rel).is_file() for rel in required_files}
    checks['required_dirs'] = {rel: (home / rel).is_dir() for rel in required_dirs}

    config_path = home / 'config.yaml'
    config_ok = False
    plugin_enabled = False
    terminal_cwd = None
    if config_path.exists() and yaml is not None:
        try:
            cfg = yaml.safe_load(config_path.read_text(encoding='utf-8')) or {}
            config_ok = True
            enabled = ((cfg.get('plugins') or {}).get('enabled') or [])
            plugin_enabled = 'memfirst-realtime' in enabled
            terminal_cwd = (cfg.get('terminal') or {}).get('cwd')
        except Exception as exc:
            checks['config_error'] = repr(exc)
    checks['config_yaml'] = config_ok
    checks['plugin_enabled'] = plugin_enabled
    checks['terminal_cwd'] = terminal_cwd

    l0_seed = sorted((home / 'memory/l0/intake/sessions').glob('*_onboarding.jsonl')) if (home / 'memory/l0/intake/sessions').exists() else []
    root_seed = sorted((home / 'sessions').glob('*_onboarding.jsonl')) if (home / 'sessions').exists() else []
    checks['l0_onboarding_seed'] = bool(l0_seed) and all(check_jsonl(p) for p in l0_seed)
    checks['root_onboarding_seed'] = bool(root_seed) and all(check_jsonl(p) for p in root_seed)

    plugin_init = home / 'plugins/memfirst-realtime/__init__.py'
    text = plugin_init.read_text(encoding='utf-8', errors='ignore') if plugin_init.exists() else ''
    checks['pre_llm_hook_declared'] = 'pre_llm_call' in text and 'register_hook' in text
    checks['post_llm_hook_declared'] = 'post_llm_call' in text and 'memfirst_ingest.py' in text

    bad_identity_words = {}
    for rel in ['SOUL.md', 'MEMORY.md', 'USER.md', 'memory/l1/SOUL.md', 'memory/l1/MEMORY.md', 'memory/l1/USER.md']:
        p = home / rel
        if p.exists():
            t = p.read_text(encoding='utf-8', errors='ignore').lower()
            hits = [w for w in [' user ', ' human '] if w in f' {t} ']
            if hits:
                bad_identity_words[rel] = hits
    checks['identity_distancing_words'] = bad_identity_words

    ok = True
    for group in ['required_files', 'required_dirs']:
        ok = ok and all(checks[group].values())  # type: ignore[index,union-attr]
    ok = ok and config_ok and plugin_enabled
    ok = ok and bool(checks['l0_onboarding_seed']) and bool(checks['root_onboarding_seed'])
    ok = ok and bool(checks['pre_llm_hook_declared']) and bool(checks['post_llm_hook_declared'])
    ok = ok and not bad_identity_words
    results['ok'] = ok
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
