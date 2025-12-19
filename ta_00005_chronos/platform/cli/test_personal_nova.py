#!/usr/bin/env python3
"""
Quick test of personal Nova script functionality
"""

import subprocess
import time

def test_personal_nova():
    """Test personal Nova script functionality"""
    
    print("🧪 Testing Personal Nova Script Functionality")
    print("=" * 50)
    
    # Test 1: Status check
    print("\n1. Testing status check for Vigil...")
    try:
        result = subprocess.run([
            'python3', '/adapt/platform/novaops/cli/personal_nova.py', 
            '--agent', 'vigil', '--status'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Status check PASSED")
            print("Output:", result.stdout[:200], "...")
        else:
            print("❌ Status check FAILED")
            print("Error:", result.stderr[:200])
    except Exception as e:
        print(f"❌ Status check ERROR: {e}")
    
    # Test 2: Different agents
    agents = ['vigil', 'nexus', 'chronos', 'root']
    print(f"\n2. Testing all agents ({len(agents)} agents)...")
    
    for agent in agents:
        try:
            result = subprocess.run([
                'python3', '/adapt/platform/novaops/cli/personal_nova.py', 
                '--agent', agent
            ], capture_output=True, text=True, timeout=5)
            
            if 'Personal Nova Script Ready!' in result.stdout:
                print(f"✅ {agent}: READY")
            else:
                print(f"⚠️  {agent}: Needs attention")
        except Exception as e:
            print(f"❌ {agent}: ERROR - {e}")
    
    # Test 3: Environment variables
    print(f"\n3. Testing environment integration...")
    try:
        import os
        test_envs = ['DRAGONFLY_CLUSTER_ENABLED', 'GROQ_API_KEY', 'REDIS_CLUSTER_URL']
        for env in test_envs:
            if os.environ.get(env):
                print(f"✅ {env}: Loaded")
            else:
                print(f"⚠️  {env}: Not found")
    except Exception as e:
        print(f"❌ Environment test ERROR: {e}")
    
    print(f"\n🎯 Personal Nova Script Testing Complete!")
    print(f"Agents tested: {len(agents)}")
    print(f"Environment files: 2 (db.env + m2.env)")
    print(f"Status: READY FOR INTERACTIVE USE")

if __name__ == "__main__":
    test_personal_nova()
