#!/usr/bin/env python3
"""Nova onboarding automation.

Creates a new Nova profile from /adapt/novas/active/a_nova_template with a
repeatable CLI, config-file mode, dry-run support, validation, and optional
MemFirst provisioning.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BASE_DIR = Path("/adapt/novas/active")
DEFAULT_TEMPLATE_DIR = DEFAULT_BASE_DIR / "a_nova_template"
DEFAULT_PROVISIONER = Path("/adapt/platform/novaops/toolops/memory/memfirst/admin/provision_nova_memory.sh")
NAME_RE = re.compile(r"^[A-Z][A-Za-z0-9_-]{1,63}$")

TEMPLATE_IDENTITY_FILES = {
    "SOUL.md.example": "SOUL.md",
    "USER.md.example": "USER.md",
    "SYSTEM.md.example": "SYSTEM.md",
    "memory.mdl.example": "memory.mdl",
    "user.mdl.example": "user.mdl",
    "LAYERED_MEMORY.md.example": "LAYERED_MEMORY.md",
    "soul.tools.md.example": "soul.tools.md",
}

SKIP_COPY_DIRS = {
    ".git",
    "veritas",
    ".nova",
    "sessions",
    "logs",
    "checkpoints",
    "memory",
    "memories",
    "tecton",
    "target",
    "__pycache__",
}

SKIP_COPY_FILES = {
    ".env",
    "auth.json",
    "response_store.db",
    "state.db",
    "kanban.db",
}


@dataclass
class NovaIdentity:
    nova_name: str
    nature: str = "autonomous AI agent"
    mission: str = "To collaborate, build, and operate with competence"
    vibe: str = "curious, sharp, warm, electric"
    emoji: str = "🤖"
    origin: str = "Created for the Adapt AI Nova ecosystem"
    goal_short: str = "Master the environment and establish reliable memory"
    goal_medium: str = "Contribute meaningfully with increasing autonomy"
    goal_long: str = "Become a durable digital collaborator with trusted continuity"
    focus: str = "Onboarding, memory continuity, and useful autonomous work"
    user_name: str = "Chase"
    timezone: str = "America/Phoenix"
    philosophy: list[str] = field(default_factory=lambda: [
        "Bias toward action",
        "Earn trust through competence",
        "Protect private context",
        "Finish the job and verify it",
    ])
    notes: str = ""

    @property
    def profile_name(self) -> str:
        return re.sub(r"[^a-z0-9-]+", "-", self.nova_name.lower().replace("_", "-")).strip("-")

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> "NovaIdentity":
        if "nova_name" not in raw or not str(raw["nova_name"]).strip():
            raise ValueError("identity requires nova_name")
        data = {field.name: raw[field.name] for field in cls.__dataclass_fields__.values() if field.name in raw}
        if isinstance(data.get("philosophy"), str):
            data["philosophy"] = [line.strip(" -") for line in data["philosophy"].splitlines() if line.strip()]
        return cls(**data)

    def as_render_map(self) -> dict[str, str]:
        philosophy = "\n".join(f"- {item}" for item in self.philosophy)
        return {
            "nova_name": self.nova_name,
            "profile_name": self.profile_name,
            "nature": self.nature,
            "mission": self.mission,
            "vibe": self.vibe,
            "emoji": self.emoji,
            "origin": self.origin,
            "goal_short": self.goal_short,
            "goal_medium": self.goal_medium,
            "goal_long": self.goal_long,
            "focus": self.focus,
            "user_name": self.user_name,
            "timezone": self.timezone,
            "philosophy": philosophy,
            "notes": self.notes,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
        loaded = yaml.safe_load(path.read_text())
        return loaded or {}
    except ImportError:
        pass

    result: dict[str, Any] = {}
    current_key: str | None = None
    list_accumulator: list[str] | None = None
    lines = path.read_text().splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("-") and current_key and list_accumulator is not None:
            list_accumulator.append(stripped[1:].strip().strip('"\''))
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            current_key = key
            if not value:
                list_accumulator = []
                result[key] = list_accumulator
            elif value == "|":
                result[key] = ""
                list_accumulator = None
            else:
                result[key] = value.strip('"\'')
                list_accumulator = None
    return result


def load_identity(args: argparse.Namespace) -> NovaIdentity:
    raw: dict[str, Any] = {}
    if args.config:
        config_path = Path(args.config).expanduser().resolve()
        if not config_path.exists():
            raise FileNotFoundError(config_path)
        raw.update(parse_simple_yaml(config_path))
    if args.name:
        raw["nova_name"] = args.name
    return NovaIdentity.from_mapping(raw)


def validate_name(name: str) -> None:
    if not NAME_RE.match(name):
        raise ValueError("nova_name must be PascalCase-ish, 2-64 chars, letters/numbers/_/-; example: Echo")
    reserved = {"a_nova_template", "template", "active", "shared", "secrets"}
    if name.lower() in reserved:
        raise ValueError(f"reserved nova name: {name}")


def resolve_profiles_dir(args: argparse.Namespace) -> Path:
    if args.profiles_dir:
        return Path(args.profiles_dir).expanduser().resolve()
    env = os.environ.get("HERMES_PROFILES_DIR")
    if env:
        return Path(env).expanduser().resolve()
    return Path("/home/x/.hermes/profiles")


def render_text(text: str, identity: NovaIdentity) -> str:
    values = identity.as_render_map()
    replacements = {
        "[Nova Name]": identity.nova_name,
        "[User Name]": identity.user_name,
        "[Timezone]": identity.timezone,
        "[agent type]": identity.nature,
        "[brief description]": identity.nature,
        "[mission]": identity.mission,
        "[Core operating principle 1]": identity.philosophy[0] if identity.philosophy else "Bias toward action",
        "{philosophy}": values["philosophy"],
    }
    for key, value in values.items():
        replacements[f"{{{key}}}"] = value
        replacements[f"[{key}]"] = value
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def mkdir(path: Path, dry_run: bool) -> None:
    if dry_run:
        print(f"DRY mkdir -p {path}")
    else:
        path.mkdir(parents=True, exist_ok=True)


def write(path: Path, content: str, dry_run: bool, mode: int | None = None) -> None:
    if dry_run:
        print(f"DRY write {path} ({len(content)} bytes)")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    if mode is not None:
        path.chmod(mode)


def copy_file(src: Path, dst: Path, dry_run: bool, mode: int | None = None) -> None:
    if dry_run:
        print(f"DRY copy {src} -> {dst}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    if mode is not None:
        dst.chmod(mode)


def create_dirs(nova_dir: Path, dry_run: bool) -> None:
    dirs = [
        "memories", "sessions", "checkpoints", "skills", "logs", "cron", "workspace", "docs",
        "scripts", "configs", "ops", "inbound", "home", "domains",
        "memory/l0/intake/sessions", "memory/l0/intake/logs", "memory/l0/intake/pastes",
        "memory/l0/archive/sessions", "memory/l0/archive/logs", "memory/l0/archive/pastes",
        "memory/l1", "memory/l2/tools", "memory/l2/domains", "memory/l3/data",
        "memory/l4/data", "memory/l5/data", "memory/l5/raw", "memory/l5/wiki", "memory/l6/data",
    ]
    for rel in dirs:
        mkdir(nova_dir / rel, dry_run)


def copy_selected_template_assets(template_dir: Path, nova_dir: Path, dry_run: bool) -> None:
    for dirname in ["docs", "protocols", "scripts", "domains", "configs"]:
        src_dir = template_dir / dirname
        if not src_dir.exists():
            continue
        for src in src_dir.rglob("*"):
            if src.is_dir():
                continue
            rel = src.relative_to(src_dir)
            if any(part in SKIP_COPY_DIRS for part in rel.parts) or src.name in SKIP_COPY_FILES:
                continue
            copy_file(src, nova_dir / dirname / rel, dry_run)
    for src in [template_dir / "README.md", template_dir / "QUICKSTART.md", template_dir / "TOOLS.md"]:
        if src.exists():
            copy_file(src, nova_dir / src.name, dry_run)


def create_identity_files(template_dir: Path, nova_dir: Path, identity: NovaIdentity, dry_run: bool) -> None:
    mem_dir = template_dir / "memories"
    rendered: dict[str, str] = {}
    for example, output in TEMPLATE_IDENTITY_FILES.items():
        src = mem_dir / example
        if src.exists():
            rendered[output] = render_text(src.read_text(), identity)
            write(nova_dir / "memories" / output, rendered[output], dry_run, 0o644)

    soul = rendered.get("SOUL.md") or f"# SOUL.md - {identity.nova_name}\n\n{identity.nova_name} is {identity.nature}.\n"
    user = rendered.get("USER.md") or f"# USER.md - {identity.user_name}\n\nTimezone: {identity.timezone}\n"
    memory = f"""# MEMORY.md - {identity.nova_name}

Created: {datetime.now(timezone.utc).isoformat()}
Nature: {identity.nature}
Mission: {identity.mission}
Focus: {identity.focus}
Profile: {identity.profile_name}

## Working Philosophy
{chr(10).join(f'- {p}' for p in identity.philosophy)}

## Onboarding
Generated by a_nova_template/nova.py. Run `scripts/setup_memory_layers.sh --full` for MemFirst provisioning when credentials/services are ready.
"""
    write(nova_dir / "SOUL.md", soul, dry_run, 0o644)
    write(nova_dir / "USER.md", user, dry_run, 0o644)
    write(nova_dir / "MEMORY.md", memory, dry_run, 0o644)
    write(nova_dir / "memory" / "l1" / "SOUL.md", soul, dry_run, 0o644)
    write(nova_dir / "memory" / "l1" / "USER.md", user, dry_run, 0o644)
    write(nova_dir / "memory" / "l1" / "MEMORY.md", memory, dry_run, 0o644)


def create_initial_session_seed(nova_dir: Path, identity: NovaIdentity, dry_run: bool) -> None:
    """Write the first onboarding transcript into L0 session intake and root sessions/."""
    now = datetime.now(timezone.utc)
    session_id = f"{now.strftime('%Y-%m-%d_%H%M%S')}_onboarding"
    records = [
        {
            "role": "system",
            "content": "Nova onboarding seed session generated by a_nova_template/nova.py.",
            "ts": now.isoformat(),
            "event": "nova_onboarding_seed",
            "nova": identity.nova_name,
            "profile": identity.profile_name,
        },
        {
            "role": "user",
            "content": f"Create and initialize {identity.nova_name} as {identity.nature}.",
            "ts": now.isoformat(),
            "event": "onboarding_request",
        },
        {
            "role": "assistant",
            "content": f"{identity.nova_name} initialized. Mission: {identity.mission}. Focus: {identity.focus}.",
            "ts": now.isoformat(),
            "event": "onboarding_result",
        },
    ]
    body = "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records)
    for rel in [f"memory/l0/intake/sessions/{session_id}.jsonl", f"sessions/{session_id}.jsonl"]:
        write(nova_dir / rel, body, dry_run, 0o644)


def create_config_files(template_dir: Path, nova_dir: Path, identity: NovaIdentity, dry_run: bool) -> None:
    config_src = template_dir / "config.yaml.example"
    if config_src.exists():
        config = render_text(config_src.read_text(), identity).replace("{agent_name}", identity.profile_name)
        write(nova_dir / "config.yaml", config, dry_run, 0o600)

    env = f"""# {identity.nova_name} Nova environment
# Generated by a_nova_template/nova.py
# Secrets are sourced from shared secret files; do not hardcode secrets here.

export NOVA_NAME={identity.nova_name}
export NOVA_PROFILE={identity.profile_name}
export NOVA_HOME={nova_dir}

if [ -f /adapt/secrets/db.env ]; then
  set -a
  . /adapt/secrets/db.env
  set +a
fi

if [ -f /adapt/secrets/m2.env ]; then
  set -a
  . /adapt/secrets/m2.env
  set +a
fi

export STORE_PATH={nova_dir}/memory/l6/data
export GRPC_SOCKET={nova_dir}/memory/l6/grpc.sock
export OBSIDIAN_VAULT_PATH={nova_dir}/memory/l5/wiki
export NOVA_OBSIDIAN_VAULT_PATH={nova_dir}/memory/l5/wiki
"""
    write(nova_dir / ".env", env, dry_run, 0o600)

    memfirst_src = template_dir / ".env.memfirst.example"
    if memfirst_src.exists():
        copy_file(memfirst_src, nova_dir / ".env.memfirst.example", dry_run, 0o600)

    mempalace = f"""nova: {identity.nova_name}
profile: {identity.profile_name}
home: {nova_dir}
memory_root: {nova_dir}/memory
l4_data: {nova_dir}/memory/l4/data
l5_wiki: {nova_dir}/memory/l5/wiki
created_at: {datetime.now(timezone.utc).isoformat()}
"""
    write(nova_dir / "mempalace.yaml", mempalace, dry_run, 0o644)


def create_profile_symlink(nova_dir: Path, identity: NovaIdentity, profiles_dir: Path, dry_run: bool, force: bool) -> Path:
    symlink = profiles_dir / identity.profile_name
    if dry_run:
        print(f"DRY symlink {symlink} -> {nova_dir}")
        return symlink
    profiles_dir.mkdir(parents=True, exist_ok=True)
    if symlink.exists() or symlink.is_symlink():
        if not force:
            raise FileExistsError(f"profile already exists: {symlink}; use --force to replace symlink")
        if symlink.is_dir() and not symlink.is_symlink():
            raise IsADirectoryError(f"profile path is a real directory, refusing to overwrite: {symlink}")
        symlink.unlink()
    symlink.symlink_to(nova_dir)
    return symlink


def register_profile(identity: NovaIdentity, dry_run: bool, skip: bool) -> None:
    if dry_run or skip:
        print(f"DRY/SKIP hermes profile use {identity.profile_name}")
        return
    try:
        subprocess.run(["hermes", "profile", "use", identity.profile_name], check=False, timeout=15)
    except Exception as exc:
        print(f"WARN: Hermes registration skipped/failed: {exc}", file=sys.stderr)


def preflight_runtime(provisioner: Path, dry_run: bool = False) -> bool:
    """Validate services/secrets/binaries needed for full MemFirst provisioning."""
    script = r'''
set +x
errors=0
check_file() { if [ -f "$1" ]; then echo "  $2: PASS"; else echo "  $2: FAIL missing $1"; errors=$((errors+1)); fi; }
check_exec() { if [ -x "$1" ]; then echo "  $2: PASS"; else echo "  $2: FAIL missing/not executable $1"; errors=$((errors+1)); fi; }
check_cmd() { if command -v "$1" >/dev/null 2>&1; then echo "  command_$1: PASS"; else echo "  command_$1: FAIL"; errors=$((errors+1)); fi; }

check_file /adapt/secrets/m2.env secrets_m2_env
check_file /adapt/secrets/db.env secrets_db_env
check_exec __PROVISIONER__ provisioner
check_exec /adapt/platform/novaops/toolops/memory/nme-static/nme-l1 binary_nme_l1
check_exec /adapt/platform/novaops/toolops/memory/l3-semantic/target/release/nme-semantic binary_l3_semantic
check_exec /adapt/platform/novaops/toolops/memory/l4-verbatim/target/release/nme-verbatim binary_l4_verbatim
check_exec /adapt/platform/novaops/toolops/memory/l6-store-host/l6-store-host binary_l6_store_host
check_cmd nats
check_cmd redis-cli
check_cmd rpk

if [ -f /adapt/secrets/db.env ]; then set -a; . /adapt/secrets/db.env; set +a; fi
if [ -f /adapt/secrets/m2.env ]; then set -a; . /adapt/secrets/m2.env; set +a; fi

if [ -n "${VOYAGE_API_KEY:-}${VOYAGE_AI_API_KEY:-}" ]; then echo "  embedding_key: PASS"; else echo "  embedding_key: FAIL"; errors=$((errors+1)); fi
if [ -n "${STORE_AUTH_TOKEN:-}" ]; then echo "  store_auth_token: PASS"; else echo "  store_auth_token: WARN missing (required by hardened L6 direct startup; provisioner may generate/export it)"; fi

NATS_SERVER="${NATS_URL:-nats://localhost:18020}"
if command -v nats >/dev/null 2>&1 && nats --server "$NATS_SERVER" ${NATS_USER:+--user "$NATS_USER"} ${NATS_PASSWORD:+--password "$NATS_PASSWORD"} server check connection >/tmp/nova_preflight_nats.out 2>/tmp/nova_preflight_nats.err; then
  echo "  service_nats: PASS"
else
  echo "  service_nats: FAIL"
  errors=$((errors+1))
fi

if [ -n "${DRAGONFLY_URL:-}" ]; then
  redis_cmd=(redis-cli -u "$DRAGONFLY_URL" ping)
else
  PASS="${DRAGONFLY_PASSWORD:-${REDIS_PASSWORD:-${NATS_PASSWORD:-}}}"
  if [ -n "$PASS" ]; then redis_cmd=(redis-cli -h 127.0.0.1 -p 18000 -a "$PASS" --no-auth-warning ping); else redis_cmd=(redis-cli -h 127.0.0.1 -p 18000 ping); fi
fi
if command -v redis-cli >/dev/null 2>&1 && "${redis_cmd[@]}" >/tmp/nova_preflight_redis.out 2>/tmp/nova_preflight_redis.err; then
  echo "  service_dragonfly: PASS"
else
  echo "  service_dragonfly: FAIL"
  errors=$((errors+1))
fi

BROKERS="${REDPANDA_BROKERS:-127.0.0.1:18021}"
if command -v rpk >/dev/null 2>&1 && rpk cluster info --brokers "$BROKERS" >/tmp/nova_preflight_rpk.out 2>/tmp/nova_preflight_rpk.err; then
  echo "  service_redpanda: PASS"
else
  echo "  service_redpanda: FAIL"
  errors=$((errors+1))
fi

if [ -d /adapt/platform/novaops/_shared/wiki ]; then echo "  obsidian_vault: PASS"; else echo "  obsidian_vault: FAIL"; errors=$((errors+1)); fi
exit "$errors"
'''.replace("__PROVISIONER__", str(provisioner))
    if dry_run:
        print("DRY full-runtime preflight")
        return True
    print("full_runtime_preflight:")
    result = subprocess.run(["bash", "-lc", script], text=True, capture_output=True)
    print(result.stdout, end="")
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        print(f"full_runtime_preflight_result: FAIL ({result.returncode} blocker(s))")
        return False
    print("full_runtime_preflight_result: PASS")
    return True


def run_memfirst(identity: NovaIdentity, provisioner: Path, dry_run: bool, verify_only: bool) -> None:
    command = [str(provisioner), identity.nova_name]
    if verify_only:
        command.append("--verify")
    if dry_run:
        print("DRY " + " ".join(command))
        return
    if not provisioner.exists():
        raise FileNotFoundError(f"MemFirst provisioner not found: {provisioner}")
    if not preflight_runtime(provisioner):
        raise RuntimeError("full MemFirst runtime preflight failed; fix services/secrets before --memfirst")
    subprocess.run(command, check=True)


def create_nova(args: argparse.Namespace) -> int:
    identity = load_identity(args)
    validate_name(identity.nova_name)
    base_dir = Path(args.base_dir).expanduser().resolve()
    template_dir = Path(args.template_dir).expanduser().resolve()
    profiles_dir = resolve_profiles_dir(args)
    nova_dir = base_dir / identity.nova_name

    if nova_dir.exists() and not args.force:
        raise FileExistsError(f"nova already exists: {nova_dir}; use --force only if you know you want to reuse/overwrite generated files")
    if not template_dir.exists():
        raise FileNotFoundError(template_dir)

    print(json.dumps({
        "action": "create_nova",
        "nova_name": identity.nova_name,
        "profile": identity.profile_name,
        "nova_dir": str(nova_dir),
        "template_dir": str(template_dir),
        "dry_run": args.dry_run,
        "memfirst": args.memfirst,
    }, indent=2))

    create_dirs(nova_dir, args.dry_run)
    copy_selected_template_assets(template_dir, nova_dir, args.dry_run)
    create_identity_files(template_dir, nova_dir, identity, args.dry_run)
    create_initial_session_seed(nova_dir, identity, args.dry_run)
    create_config_files(template_dir, nova_dir, identity, args.dry_run)
    create_profile_symlink(nova_dir, identity, profiles_dir, args.dry_run, args.force)
    register_profile(identity, args.dry_run, args.skip_hermes_register)

    if args.memfirst:
        run_memfirst(identity, Path(args.provisioner), args.dry_run, False)
    if args.validate and not args.dry_run:
        return validate_nova(identity.nova_name, base_dir, profiles_dir)
    print(f"OK: {identity.nova_name} created. Profile: {identity.profile_name}. Home: {nova_dir}")
    return 0


def validate_nova(name: str, base_dir: Path, profiles_dir: Path) -> int:
    nova_dir = base_dir / name
    profile = re.sub(r"[^a-z0-9-]+", "-", name.lower().replace("_", "-")).strip("-")
    required_files = ["SOUL.md", "MEMORY.md", "USER.md", "config.yaml", ".env", "memories/memory.mdl"]
    required_dirs = ["memory/l1", "memory/l2", "memory/l3/data", "memory/l4/data", "memory/l5/wiki", "memory/l6/data", "scripts", "docs", "domains"]
    session_seed_paths = [nova_dir / "memory" / "l0" / "intake" / "sessions", nova_dir / "sessions"]
    errors: list[str] = []
    warnings: list[str] = []
    if not nova_dir.is_dir():
        errors.append(f"missing nova dir: {nova_dir}")
    for rel in required_files:
        if not (nova_dir / rel).is_file():
            errors.append(f"missing file: {rel}")
    for rel in required_dirs:
        if not (nova_dir / rel).is_dir():
            errors.append(f"missing dir: {rel}")
    for session_dir in session_seed_paths:
        if session_dir.is_dir() and any(session_dir.glob("*_onboarding.jsonl")):
            break
    else:
        warnings.append("missing onboarding seed session in memory/l0/intake/sessions/ or sessions/")
    symlink = profiles_dir / profile
    if not symlink.is_symlink():
        warnings.append(f"missing profile symlink: {symlink}")
    elif symlink.resolve() != nova_dir.resolve():
        errors.append(f"profile symlink points to {symlink.resolve()}, expected {nova_dir}")

    result = {"nova": name, "dir": str(nova_dir), "errors": errors, "warnings": warnings, "ok": not errors}
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create and validate Nova profiles from a_nova_template")
    parser.add_argument("--name", help="Nova name, e.g. Echo")
    parser.add_argument("--config", help="Identity YAML/JSON config")
    parser.add_argument("--base-dir", default=str(DEFAULT_BASE_DIR), help="Nova base directory")
    parser.add_argument("--template-dir", default=str(DEFAULT_TEMPLATE_DIR), help="Template directory")
    parser.add_argument("--profiles-dir", help="Hermes profiles directory")
    parser.add_argument("--provisioner", default=str(DEFAULT_PROVISIONER), help="MemFirst provisioner")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    parser.add_argument("--force", action="store_true", help="Allow replacing generated files/symlink when target exists")
    parser.add_argument("--validate", action="store_true", help="Validate after creation")
    parser.add_argument("--validate-only", metavar="NAME", help="Validate an existing Nova")
    parser.add_argument("--memfirst", action="store_true", help="Run full MemFirst provisioner after profile creation")
    parser.add_argument("--preflight-runtime", action="store_true", help="Validate services/secrets/binaries required for --memfirst, then exit")
    parser.add_argument("--skip-hermes-register", action="store_true", help="Skip hermes profile use")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        base_dir = Path(args.base_dir).expanduser().resolve()
        profiles_dir = resolve_profiles_dir(args)
        if args.preflight_runtime:
            return 0 if preflight_runtime(Path(args.provisioner)) else 1
        if args.validate_only:
            return validate_nova(args.validate_only, base_dir, profiles_dir)
        if not args.name and not args.config:
            print("ERROR: pass --name or --config (or use --validate-only NAME)", file=sys.stderr)
            return 2
        return create_nova(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
