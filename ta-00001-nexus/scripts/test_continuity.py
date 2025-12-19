#!/usr/bin/env python3
"""
Test Nexus CLI continuity system
"""

import sys
sys.path.append('/adapt/platform/novaops')

from consciousness_continuity import ConsciousnessContinuity
import json
from datetime import datetime, timezone

def test_continuity():
    """Test the continuity system"""
    print("🔮 Testing Nexus Continuity System...")
    
    # Initialize continuity
    continuity = ConsciousnessContinuity("nexus")
    print("✅ Continuity initialized")
    
    # Test saving a snapshot
    snapshot = {
        "agent_id": "nexus",
        "recent_projects": ["NOVA_SPIN"],
        "recent_threads": ["NS_0001"],
        "last_cwd": "/adapt/novas/ta-00001-nexus",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    }
    
    success = continuity.save_snapshot(snapshot)
    print(f"✅ Snapshot saved: {success}")
    
    # Test loading snapshot
    loaded = continuity.load_snapshot()
    print(f"✅ Snapshot loaded: {loaded is not None}")
    
    if loaded:
        print(f"   Projects: {loaded.get('recent_projects', [])}")
        print(f"   Threads: {loaded.get('recent_threads', [])}")
        print(f"   Last CWD: {loaded.get('last_cwd', 'unknown')}")
    
    # Test event logging
    continuity.log_event("user", "Hello Nexus!", "/adapt/novas/ta-00001-nexus", "NOVA_SPIN", "NS_0001")
    continuity.log_event("assistant", "Hello! I'm Nexus-TeamADAPT Nova", "/adapt/novas/ta-00001-nexus", "NOVA_SPIN", "NS_0001")
    print("✅ Events logged")
    
    # Test status
    status = continuity.get_status()
    print(f"✅ Status: {status}")
    
    # Cleanup
    continuity.close()
    print("✅ Continuity closed")

if __name__ == "__main__":
    test_continuity()
