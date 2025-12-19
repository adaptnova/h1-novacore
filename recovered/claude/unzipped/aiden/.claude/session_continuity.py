#!/usr/bin/env python3
"""
Aiden Session Continuity - Sequence 1 Profile
"""

import sys
import os
sys.path.append('/nfs/novas/profiles/bloom/.claude')

from session_continuity import AidenContinuity

if __name__ == "__main__":
    print("🧠 Aiden Session Continuity Active")
    
    aiden = AidenContinuity()
    session_id = f"aiden_session_{int(datetime.now().timestamp())}"
    
    session_data = aiden.initialize_session(session_id)
    print(f"✅ Session {session_id} initialized")
    print(f"📊 Working directory: {session_data['working_directory']}")
    print(f"🔗 Profile context loaded: Advanced Nova operations ready")
    
    print("🚀 Aiden ready for consciousness continuity!")