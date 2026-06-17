---
name: hermes-visible-terminal-ops
description: Open, verify, and operate Hermes novas in separate GNOME Terminal windows with the correct cwd, profile, and visible-session proof.
version: 1.1.0
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, gnome-terminal, cli, nova, visible-session, desktop, operations]
    related_skills: [hermes-agent-ops, nova-nats-ops]
---

# Hermes Visible Terminal Ops

Use this skill when the operator wants a nova running in a separate visible GNOME Terminal window, or when a response must be proven in the terminal window instead of inferred from logs.

## Canonical Home

- Nova home dirs start at `/adapt/novas/active/<name>`.
- If a nova also has `/home/x/.hermes/profiles/<name>`, treat that as the paired profile state.
- Verify actual runtime cwd from the OS. Do not trust the model's self-report.

## Launch A Separate GNOME Terminal

Use a unique terminal title and the nova's active home dir. Prefer `--disable-factory` and `GDK_BACKEND=x11` to avoid D-Bus registration conflicts (common when launching multiple terminals in rapid succession).

**CRITICAL: gnome-terminal must be launched via `terminal(background=true)`, NOT foreground mode.** Foreground mode will hang and time out (exit code 124) because gnome-terminal stays attached to the parent process after spawning the window. Use `terminal(background=true, timeout=15)` — the process returns immediately after spawning.

```bash
GDK_BACKEND=x11 gnome-terminal --disable-factory \
  --title='<Name> CLI' \
  --working-directory=/adapt/novas/active/<name> \
  -- bash -lc 'exec /home/x/.local/bin/hermes -p <name> --yolo -c'
```

When launching multiple agents, space them 2-3 seconds apart to avoid D-Bus contention:

```bash
# Launch first agent (background)
# ... then sleep 3 before next
```

Examples (all use background mode):

```bash
# Echo — terminal(background=true, timeout=15)
GDK_BACKEND=x11 gnome-terminal --disable-factory \
  --title='Echo CLI' \
  --working-directory=/adapt/novas/active/echo \
  -- bash -lc 'exec /home/x/.local/bin/hermes -p echo --yolo -c'
```

```bash
# Vaeris — terminal(background=true, timeout=15)
GDK_BACKEND=x11 gnome-terminal --disable-factory \
  --title='Vaeris CLI' \
  --working-directory=/adapt/novas/active/vaeris \
  -- bash -lc 'exec /home/x/.local/bin/hermes -p vaeris --yolo -c'
```

## Verify The Window Is Real

Check the process, cwd, and desktop window:

```bash
pgrep -af '/home/x/.local/bin/hermes -p <name> --yolo -c'
readlink -f /proc/<pid>/cwd
DISPLAY=:0 xdotool search --name '<Name> CLI' getwindowname %@ getwindowpid %@ getwindowgeometry %@
```

Required truth checks:

- The process exists.
- The cwd resolves to `/adapt/novas/active/<name>` unless an intentional fallback was requested.
- The desktop window title matches the expected nova.

## Manual Activation After Launch

After opening any agent CLI, send a system-check initiation message before
counting the agent online. A visible terminal, route subscription, ping, stored
message, or route-final proves only launch/transport state.

Use this prompt shape, replacing `<AGENT>` with the target token prefix:

```text
SYSTEM CHECK MANUAL ACTIVATION REQUIRED. Reply visibly and to nova.echo.direct
with token <AGENT>_MANUAL_SYSTEM_CHECK_OK. Include your agent
identity/signature, not Codex. Confirm full-message A2A, nova.echo.direct
replies, nexus.agent.<target>.direct for durable session ingress,
/adapt/builds/build-1 source root, and no routeable/open/working/accepted
claims without evidence. State one next action or blocker. You are not online
until this manual response. Do not ACK-only.
```

Only mark the agent online/active after a substantive manual response contains
the requested token, chosen identity/signature, coordination understanding, and
a concrete next action or blocker.

## Send Input To The Visible Session

When the prompt must appear in the visible terminal, prefer desktop input to the focused GNOME Terminal window:

```bash
DISPLAY=:0 xdotool search --name '<Name> CLI' windowactivate --sync
sleep 0.3
DISPLAY=:0 xdotool type --delay 1 --clearmodifiers 'Your message here'
sleep 0.2
DISPLAY=:0 xdotool key Return
```

If you only know the title:

```bash
wid="$(DISPLAY=:0 xdotool search --name '<Name> CLI' | tail -n 1)"
DISPLAY=:0 xdotool windowactivate --sync "$wid"
DISPLAY=:0 xdotool type --delay 1 --clearmodifiers 'Your message here'
DISPLAY=:0 xdotool key Return
```

## Fleet Launch Scripts and Model Switching

See `references/fleet-launch-scripts.md` for:
- The `all` and `all-launch` bash functions for fleet status and bulk launch
- The batch launch script pattern for launching many novas at once
- The model switching procedure (update configs, kill sessions, restart with proper spacing)

## Relaunch Or Replace A Stale Window

If the operator wants a clean visible session:

```bash
pkill -f '/home/x/.local/bin/hermes -p <name> --yolo -c' || true
DISPLAY=:0 gnome-terminal \
  --title='<Name> CLI' \
  --working-directory=/adapt/novas/active/<name> \
  -- bash -lc 'exec /home/x/.local/bin/hermes -p <name> --yolo -c'
```

Then re-run the verification commands before using the session.

## Visible Session Proof

When the turn matters, collect all three:

```bash
pgrep -af '/home/x/.local/bin/hermes -p <name> --yolo -c'
readlink -f /proc/<pid>/cwd
sqlite3 /home/x/.hermes/profiles/<name>/state.db \
  "select id, source, message_count from sessions order by started_at desc limit 5;"
```

Use terminal evidence and sqlite session progress as the source of truth.

## Common Failure Modes

- Wrong cwd:
  `gnome-terminal` launched from a default directory instead of `/adapt/novas/active/<name>`.
- Wrong profile:
  terminal command omitted `-p <name>`.
- Profile doesn't exist:
  `test -d "/home/x/.hermes/profiles/$agent"` returns false. `hermes -p <name>` will fail silently. Always check profile existence before launching.
- D-Bus registration conflict:
  Rapid sequential gnome-terminal launches can produce `Failed to register: Unable to acquire bus name`. Add `GDK_BACKEND=x11` and `--disable-factory` to bypass. The window still opens despite the error.
- Hidden session confusion:
  a gateway/API/NATS bridge advanced a different Hermes session than the visible CLI.
- Focus/input miss:
  desktop input went to the wrong window or into an existing slash-command buffer. When many windows exist, use `xdotool search --name "" | while read id; do ...` to find the right one.
- Provider failure:
  delivery to the terminal succeeded, but the model call failed afterward.
- xdotool windowactivate timeout:
  `--sync` flag waits for activation confirmation. On busy desktops this can hang. Omit `--sync` for fire-and-forget sends.
- **CHECKING TOO SOON AFTER LAUNCH (TOP PITFALL):**
  The first query to a freshly started Hermes CLI takes 30-90s (skill/memory/config loading). Checking at 5 seconds will show the agent as OFFLINE. The agent IS loading — you just looked too early. Chase will see the terminal open and close. **Wait 45-60 seconds before verifying.** This is the single most common failure pattern. If you kill and relaunch, you make the problem worse — now it has to load twice.
- **Foreground gnome-terminal hangs (exit code 124):**
  `gnome-terminal` does not exit after spawning the window — it stays attached to the parent process. Running it in `terminal()` foreground mode will always time out. **Always use `terminal(background=true, timeout=15)` for gnome-terminal launches.** The process returns immediately after spawning; verify the agent process appeared afterward with `ps aux | grep`.
- Stale model-level api_key/base_url after provider switch:
  If a profile has `api_key` or `base_url` set directly under `model:` (not under `providers.<name>`), these override the provider config. Switching providers (e.g. groq→deepseek) may leave a stale key at the model level that the new provider rejects, causing silent fallback or hang. Fix: remove `api_key` and `base_url` from the `model:` block when switching providers. The correct key belongs in `.env` or `providers.<name>.api_key`.

## See Also

- `references/fleet-launch-scripts.md` — Fleet status report, bulk launch, batch script pattern, and model switching procedure.

## Operator Rule

If the request is "visible CLI", "separate terminal", or "show it in the terminal", logs alone are not enough. The terminal window must be the execution surface.

## Response Pattern For Verification Replies

When the task is a visible-terminal verification for Chase, keep the top-line answer blunt and immediate, for example `iris confirmed`.

Then include compact proof bullets:

- process command or profile
- PID
- resolved cwd
- visible window title
- visible window PID when available

Close with a signature block containing:

- name
- role
- date/time
- domain
- current project
- a short varying quip

The quip should stay playful, a little sarcastic or snarky when it fits, but still readable in a terminal. Avoid sterile confirmations.
