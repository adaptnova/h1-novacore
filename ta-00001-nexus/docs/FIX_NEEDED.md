# 🚨 FIX REQUIRED: Enhanced CLI Not Working

## Problem Summary
Your `enhanced_cli_with_continuity.py` is trying to use a **non-existent backend** and calling **non-existent methods**. 

## Root Causes

### 1. Wrong Import Path ❌
**Current (Broken):**
```python
sys.path.append('/adapt/platform/novaops')
from history_importer import ContinuityBackend  # ❌ DOESN'T EXIST
```

**Should Be:**
```python
sys.path.append('/adapt/platform/novaops')
from consciousness_continuity import ConsciousnessContinuity  # ✅ EXISTS
```

### 2. Wrong Method Names ❌
**Current (Broken):**
```python
continuity_backend.append_event(agent_id, event)  # ❌ NO SUCH METHOD
continuity_backend.load_snapshot(agent_id)  # Wrong signature
```

**Should Be:**
```python
continuity_backend.log_event("user", user_input, str(workspace_dir), project_id, thread_id)
continuity_backend.log_event("assistant", response, str(workspace_dir), project_id, thread_id)
continuity_backend.load_snapshot()  # No parameters
```

### 3. Missing Assistant Response Logging ❌
**Current (Broken):**
- Only logs user input
- NO logging of agent/assistant responses
- Missing snapshot updates after responses

**Should Be:**
```python
# Log user message
continuity_backend.log_event("user", user_input, str(workspace_dir), project_id, thread_id)

# Run agent
response = await agent.run()

# Log assistant response
if continuity_backend and response:
    continuity_backend.log_event("assistant", str(response), str(workspace_dir), project_id, thread_id)
    
    # Update snapshot
    if current_snapshot:
        if project_id and project_id not in current_snapshot.get("recent_projects", []):
            current_snapshot.setdefault("recent_projects", []).append(project_id)
        if thread_id and thread_id not in current_snapshot.get("recent_threads", []):
            current_snapshot.setdefault("recent_threads", []).append(thread_id)
        current_snapshot["last_cwd"] = str(workspace_dir)
        current_snapshot["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
```

---

## Fixes Needed

### Fix 1: Update Import
Change line 48-55 in `enhanced_cli_with_continuity.py`:
```python
# OLD (Lines 48-55)
try:
    import sys
    sys.path.append('/adapt/platform/novaops')
    from history_importer import ContinuityBackend
except ImportError as e:
    print(f"[WARN] Consciousness continuity system not available: {e}")
    ContinuityBackend = None

# NEW (Replace with)
try:
    import sys
    sys.path.append('/adapt/platform/novaops')
    from consciousness_continuity import ConsciousnessContinuity
    CONTINUITY_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Consciousness continuity system not available: {e}")
    CONTINUITY_AVAILABLE = False
    ConsciousnessContinuity = None
```

### Fix 2: Update Backend Initialization
Change:
```python
# OLD
continuity_backend = ContinuityBackend(agent_id)

# NEW
continuity_backend = ConsciousnessContinuity(agent_id) if CONTINUITY_AVAILABLE else None
```

### Fix 3: Update Method Calls
Find and replace:
```python
# Replace ALL instances of:
continuity_backend.append_event(agent_id, event)
# With:
continuity_backend.log_event(event["type"], event["text"], event["cwd"], event["project_id"], event["thread_id"])

# Replace ALL instances of:
continuity_backend.load_snapshot(agent_id)
# With:
continuity_backend.load_snapshot()

# Add after agent.run():
response = await agent.run()
if continuity_backend and response:
    continuity_backend.log_event("assistant", str(response), str(workspace_dir), project_id, thread_id)
```

---

## Solution Options

### Option A: Fix Enhanced CLI (Recommended)
Take the **working implementation** from `/adaptai/projects/coders/m2/mini_agent/cli.py` and merge with your features:
1. Copy the `run_agent_with_continuity()` function (lines 648-990)
2. Replace your enhanced version
3. Add your custom features on top

### Option B: Use New CLI As Base
Replace `enhanced_cli_with_continuity.py` with the working version from coders/m2, then add your custom features.

### Option C: Quick Patch
Just fix the imports and method calls in your current file.

---

## Verification
Once fixed, test:
```bash
cd /adapt/novas/ta-00001-nexus
python3 enhanced_cli_with_continuity.py --agent-id nexus
# Should see: "✅ Consciousness continuity initialized"
# After chat: Events should appear in MongoDB
```

---

## Why The New CLI Works
The coders/m2 version has:
- ✅ Correct backend import (`ConsciousnessContinuity`)
- ✅ Correct method calls (`log_event`, `load_snapshot`)
- ✅ Full event logging (user + assistant)
- ✅ Proper snapshot management
- ✅ Tested and working continuity

**Your enhanced version has NONE of these working.** 

The continuity features were **never functional** in your enhanced CLI.

---

**Recommendation:** Use the coders/m2 version as your base - it's complete and working. Add your customizations on top of it.
