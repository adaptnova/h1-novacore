# 02 — Hermes Runtime + Profile Requirements

Hermes is part of onboarding, not an optional wrapper. A Nova is not fully onboarded until the Hermes profile, config, skills/runtime files, and session behavior are verified.

## Required paths

```text
/adapt/novas/active/<Name>/                    # Nova home
/home/x/.hermes/profiles/<profile>             # symlink to Nova home
/adapt/novas/active/<Name>/config.yaml         # active Hermes config
/adapt/novas/active/<Name>/.env                # profile env, sources shared secrets
/adapt/novas/active/<Name>/sessions/           # Hermes/root session mirror
/adapt/novas/active/<Name>/state.db            # Hermes session DB when runtime has started
```

## Config requirements

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
plugins:
  enabled:
    - memfirst-realtime
terminal:
  cwd: /assigned/project/repo
```

## Verification commands

```bash
python3 - <<'PY'
import yaml
from pathlib import Path
p = Path('/adapt/novas/active/<Name>/config.yaml')
yaml.safe_load(p.read_text())
print('config_yaml: PASS')
PY

readlink -f /home/x/.hermes/profiles/<profile>
hermes -p <profile> chat -q 'Reply exactly: NAME=<name>; ROLE=<role>; REPO=<repo>; FIRST=<first action>.' -Q --yolo --max-turns 1
```

## Pitfalls

- If the profile is a real directory instead of a symlink, Hermes may load stale/default identity.
- If `SOUL.md` in the profile is default Hermes boilerplate, the Nova wakes as generic Hermes.
- `terminal.cwd` affects terminal tool calls; the visible CLI process cwd still needs launch-time working-directory handling.
- Config YAML must use consistent 2-space indentation. Validate after every hand edit.
- NATS bridge, gateway NATS platform, and visible CLI are independent runtime paths; verify the one being used.
