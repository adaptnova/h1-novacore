# DSH ↔ Grok OAuth rotation (fixed 2026-08-17)

**Problem:** DSH `.credentials.yaml` held a **stale** `GROK_OAUTH_TOKEN` while `~/.grok/auth.json` had a fresher OAuth access token. Long-lived `dsh-web` + **disabled** 30m timer → stale key again.

**Source of truth:** `/home/x/.grok/auth.json` (xAI OIDC)  
**DSH sink:** `/adapt/ops/deepseek-harness/.credentials.yaml` → `GROK_OAUTH_TOKEN`  
**settings.yaml:** `apiKeyEnv: GROK_OAUTH_TOKEN` (OAuth only — no `XAI_API_KEY`)

## Sync (manual)
```bash
/adapt/ops/deepseek-harness/ops/sync-grok-oauth-to-dsh.sh
/adapt/ops/deepseek-harness/ops/sync-codex-oauth-to-dsh.sh
/adapt/ops/deepseek-harness/ops/sync-router-keys-to-dsh.sh
systemctl --user restart dsh-web.service   # pick up new creds
```

## Rotation (automatic)
- Unit: `dsh-grok-oauth-sync.timer` → every **30m** (+2m after boot)
- Service runs: grok oauth sync, codex oauth sync, router keys from `m2.env`
- Enabled 2026-08-17 (was inactive/disabled — root cause of drift)

## Law
- OAuth only for Grok/Codex on DSH
- Never put `XAI_API_KEY` / `OPENAI_API_KEY` in DSH `.env` or credentials for those providers
- After human re-login in Grok CLI, run grok sync (or wait ≤30m) + restart dsh-web if sessions still fail

— Ethos · CEEO
