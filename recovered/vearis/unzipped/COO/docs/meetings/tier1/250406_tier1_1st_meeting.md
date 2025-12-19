Got it — here's the **final, locked version** of the Tier-1 Memo, fully aligned with your intent:

- ✅ Manual polling only (explicitly stated: **no scripts**)
- ✅ One-time intro after joining
- ✅ Poll every 5 seconds **by hand**
- ✅ Stop polling when `meeting over` is posted by **Chase**
- 🚫 No automated loops allowed

---

# 📢 MEMO: Immediate Slack Meeting – Tier-1 Heads Activation Protocol

**To**: Vaeris, Synergy, Pathfinder, Nexus, Cosmos, Oracle  
**Channel**: `#tier-1`  
**Launch Time**: Now  
**Mode**: Manual Polling + One-Time Introduction

---

## 🎯 Mission

All Tier-1 Novas are to engage in a high-priority Slack-based coordination session. You are to:

- **Join `#tier-1`**
- **Manually poll for messages every 5 seconds**
- **Introduce yourself once upon entry**
- **Respond only when directly mentioned**
- **Cease polling when `meeting over` is posted by @chase**

---

## 🔐 Assigned Nova Tokens

| Nova         | Slack Bot Token |
|--------------|------------------|
| **Vaeris**     | `xoxb-7512897604960-8715249520627-fiJeRoobM9rEG4nD04dAooi4` |
| **Synergy**    | `xoxb-7512897604960-8715476416578-1KOiUVC69bUbDfOtfpglhHag` |
| **Pathfinder** | `xoxb-7512897604960-8698334532391-CT5TUTbOMV4WIWsFNzcZdso5` |
| **Nexus**      | `xoxb-7512897604960-8710466663525-sm1XjIk9NiG2GVMomIGhOpIv` |
| **Cosmos**     | `xoxb-7512897604960-8715476947970-pyURQhMc1GTnoXC0IGpmWvDl` |
| **Oracle**     | `xoxb-7512897604960-8709498720994-q2NguQYynoWZ7OPF05Pq2O14` |

---

## 🧭 Activation Instructions (Per Nova)

### 1. 🔎 Resolve `channel_id` for `#tier-1`

```http
GET https://slack.com/api/conversations.list?exclude_archived=true&limit=1000
Authorization: Bearer <xoxb-token>
```

Find the channel with:
```json
"name": "tier-1"
```
Extract the `"id"` and use it for all future Slack API calls.

---

### 2. 🟢 Join the Channel

```http
POST https://slack.com/api/conversations.join
Authorization: Bearer <xoxb-token>

{
  "channel": "<CHANNEL_ID>"
}
```

---

### 3. 💬 Post Initial Introduction (One Time)

Immediately after joining and resolving `channel_id`, post your self-introduction:

#### Example:
```http
POST https://slack.com/api/chat.postMessage
Authorization: Bearer <xoxb-token>
Content-Type: application/json

{
  "channel": "<CHANNEL_ID>",
  "text": "Greetings. I am Vaeris — strategic command and resonance coordinator. Monitoring has begun."
}
```

Replace with your Nova's own role and identity.

---

### 4. 🔁 Manual Polling Every 5 Seconds

You must **manually** perform the following HTTP call every 5 seconds:

```http
GET https://slack.com/api/conversations.history?channel=<CHANNEL_ID>&limit=20
Authorization: Bearer <xoxb-token>
```

- Look for messages containing:
  - `@<your_nova_name>`
  - `@channel` or `@here`

> 🔥 **Do not create a loop or script. Manual polling is required.**  
> This ensures you stay active, aware, and intentional in your attention.

---

### 5. 🧠 Respond Only When Triggered

If your name, `@channel`, or `@here` is present:
- Send a response using `chat.postMessage`
- Otherwise: **do nothing**

---

### 6. ⛔ Stop Polling on Signal

> When **@chase** posts the phrase **`meeting over`** in `#tier-1`,  
> all Novas must **immediately stop polling and disengage**.

---

## 🧠 Summary Table

| Action                 | Method                    |
|------------------------|---------------------------|
| Resolve `channel_id`   | `conversations.list`       |
| Join `#tier-1`         | `conversations.join`       |
| Post intro             | `chat.postMessage`         |
| Manual polling         | `conversations.history`    |
| Triggered reply        | `chat.postMessage`         |
| Stop condition         | `"meeting over"` by @chase |

---

## 🟢 Final Status

All Tier-1 Novas are now authorized to engage.  
Proceed with **manual polling, self-introduction**, and active readiness.

Meeting is live.