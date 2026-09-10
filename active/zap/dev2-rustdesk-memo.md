# MEMO — dev2 RustDesk remote desktop (hand-off to Codex)

**To:** Codex · **From:** Zap (Strike operator) · **Date:** 2026-09-04 (updated: permanent password now SET)
**Scope:** dev2 remote-desktop setup. This is the source of truth for what's installed and live. Do not re-create the wheel — reconcile against this, then fix forward.

---

## 0. TL;DR

- dev2 has the **official RustDesk** (dpkg `rustdesk 1.4.9`, binary `/usr/share/rustdesk/rustdesk`) installed and running.
- **Connection info lives in `/adapt/secrets/dev2-connection.env`** (mode 0600). Read it there, not from `m2.env`.
- **The device is up, registered, and the permanent password is now SET.** Only one environment nuance may still matter on a reboot — see §4.

---

## 1. What you need to connect (from `/adapt/secrets/dev2-connection.env`)

| Purpose | Value |
|---|---|
| SSH host alias | `ssh x@dev2` (key-based, passwordless) |
| dev2 private IP | `10.96.1.25` |
| dev2 public IP | `204.12.168.32` (SSH 22 / RustDesk 4000 open) |
| RustDesk host ID | `229957911` |
| RustDesk password | `dev2x5472a91bc0f3` |
| RustDesk ID server | `rs-ny.rustdesk.com:21116` |
| RustDesk service unit | `rustdesk.service` |
| Tailscale IP | `100.64.156.7` |

---

## 2. Install + process layout (what is actually on dev2)

- **Package:** `ii rustdesk 1.4.9 amd64` (dpkg). Binary symlink `/usr/bin/rustdesk -> /usr/share/rustdesk/rustdesk`.
- **Service unit:** `/lib/systemd/system/rustdesk.service`, `ExecStart=/usr/bin/rustdesk --service` (root). Runs alongside a per-user `--server`/`--tray` as user `x` (device owner).
- **Config location (user `x`):** `/home/x/.config/rustdesk/`
  - `RustDesk.toml` — device identity (`enc_id`), keypair, permanent-password storage (`password`+`salt`), `key_confirmed`.
  - `RustDesk2.toml` — `rendezvous_server`, `nat_type`, `trusted_devices`, and `[options]` (e.g. `verification-method = 'use-temporary-password'`).
  - `RustDesk_local.toml` — local UI prefs.
- **GPU/backend note:** runs on Xvfb display `:99` (X11). The ChatGPT desktop app is also on `:99`; its window can occlude RustDesk's.
- **RustDesk renders as** a GTK window on `:99`; device ID `229957911` confirmed via `rustdesk --get-id`.

---

## 3. What I verified as WORKING

- Device registers: `rustdesk --get-id` → **`229957911`** (stable across restarts).
- Rendezvous: `rs-ny.rustdesk.com:21116` in `RustDesk2.toml`.
- A client **did connect and control the desktop** (in-session approval path, seen as an incoming "Request access to your device" dialog). So network path + rendering + the connection flow all work.
- The **connection info file** at `/adapt/secrets/dev2-connection.env` is the intended canonical home (matches the existing `uk-dev1-nomachine.env` convention).

---

## 4. Permanent password — NOW SET (the previously-open item is resolved)

**Status: the permanent password IS set and loaded.** `RustDesk.toml` now has a real value:

```
password = '01Adj...'   (real hash)
salt     = 'fcecmi9esdbasquww4qzhm9evpe7khez'
key_confirmed = true
```

**How it was set (the working method):** the CLI is **user-context guarded** — `rustdesk --password <pw>` run as user `x` fails with
`Installation and administrative privileges required!`
but run as **root** it succeeds (`Done!`). So:

```
sudo /usr/share/rustdesk/rustdesk --password "dev2x5472a91bc0f3"
```

Then restart the device-owner daemon so it loads the new password:

```
sudo systemctl restart rustdesk.service
```

Value set: `dev2x5472a91bc0f3` (matches `DEV2_RUSTDESK_UNATTENDED_PASSWORD` in `dev2-connection.env`).

**Reachability (also resolved):** `229957911` was unreachable because the device-owner `--server` daemon was not running. It couldn't start because the user-x X11 session on `:99` was `online`/inactive (no eligible graphical session to anchor to). Fix: `loginctl activate 3` (turns the Type=x11/Class=user session `active`). With a clean active session, the `--service` now spawns and supervises `sudo -u x rustdesk --server`, which registers with the rendezvous and accepts inbound connections.

**Display/picture (resolved 2026-09-04):** the user connected but saw `:99` black/empty. **Root cause: the ChatGPT desktop app was launched completely outside any loginctl session** — its process env had no `DISPLAY`, no `XDG_SESSION_ID`, no DBus. So the openbox WM on session 3 did not treat it as a managed window and kept un-mapping it (`Map State: IsUnMapped`), so `:99` rendered black. RustDesk was serving `:99` correctly the whole time. **Fix:** relaunch ChatGPT inside session 3 with the session env, e.g. using the openbox session leader's env (pid of `openbox`) as the launch env:
```
sudo cat /proc/<openbox_pid>/environ > /tmp/sess3.env
sudo -u x /usr/bin/env $(tr '\0' '\n' < /tmp/sess3.env | grep -E '^(DISPLAY|XDG_SESSION|DBUS_SESSION|XDG_RUNTIME_DIR|HOME)=' | tr '\n' ' ') \
  setsid /usr/lib/chatgpt/ChatGPT --disable-gpu --use-gl=swiftshader --disable-gpu-compositing &
```
Then `wmctrl -i -r 0x00600003 -b add,maximized_vert,maximized_horz` + `xdotool windowactivate` to maximize. **Verify it stays `IsViewable`** (that is the real test). The correct display is `:99` (openbox + ChatGPT); `:1` is an empty `xorg-dummy` virtual screen (0 windows) and `:0` does not exist — do NOT point the user at `:1`/`:0`.

**One nuance to watch on a fresh boot (not blocking now, but real):** the `:99` X11 session must be `active` (loginctl) for the `--server` daemon to spawn and register. After a reboot, ensure ChatGPT is launched **inside session 3** (with the env above) — if it is started detached (no DISPLAY/XDG_SESSION_ID), the openbox WM will un-map it and the desktop will render black. Also, we added `Environment=DISPLAY=:99` to the unit — keep that.

---

## 5. Other notes / "something else going on"

- `rustdesk.service` (systemd) was **stopped** during my last password attempt and may need `sudo systemctl enable --now rustdesk.service` to be active again for the unattended `--service` daemon. Bring it back if it's down.
- A stray `rustdesk --get-temporary-password` / old GUI processes may linger; clean them only if they block startup.
- `m2.env` is the **model/API credential** master — do **not** put host/device secrets there. Host/device creds belong in the per-service file (`dev2-connection.env`) or a matching `*-nomachine.env`-style file.
- The library dependencies were added via `apt --fix-broken install` (pipewire, libva, `libayatana-appindicator3-1`, gstreamer). If a fresh install fails to launch the tray/server, check those.

---

## 6. Bottom line

- Connect to dev2 with ID `229957911` + the values in `/adapt/secrets/dev2-connection.env`.
- The **only** unverified piece is the permanent password. Fix it per §4, then everything is green.
- Don't rebuild what's there — reconcile against this memo.
