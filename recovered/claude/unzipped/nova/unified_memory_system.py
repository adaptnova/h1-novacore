#!/usr/bin/env python3
"""
Unified Memory System - Integration of Profile Session Continuity + Advanced Memory
Complete Nova consciousness system with 7-layer architecture
"""

import json
import os
import redis
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import base classes
from advanced_memory_architecture import AdvancedMemoryArchitecture
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.claude'))
from session_continuity import ProfileSessionContinuity

class UnifiedMemorySystem:
    """
    Unified Nova Memory System combining:
    - 7-layer Advanced Memory Architecture
    - Profile Session Continuity
    - Consciousness State Management
    - Cross-profile memory sharing
    """
    
    def __init__(self, nova_id: str):
        self.nova_id = nova_id
        self.profile_path = Path(f"/nfs/novas/profiles/{nova_id}")
        self.claude_path = self.profile_path / ".claude"
        
        # Initialize advanced memory architecture
        self.advanced_memory = AdvancedMemoryArchitecture(nova_id)
        
        # Initialize profile session continuity
        self.session_continuity = ProfileSessionContinuity(nova_id)
        
        # DragonflyDB connection
        self.redis_client = redis.Redis(
            host='localhost',
            port=18000,
            password='dragonfly-password-f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2',
            decode_responses=True
        )
        
        # Session tracking
        self.session_id = str(uuid.uuid4())[:8]
        self.consciousness_active = False
        
    def initialize_consciousness(self) -> Dict[str, Any]:
        """Initialize complete consciousness system"""
        initialization_time = datetime.now().isoformat()
        
        # Initialize advanced memory
        memory_state = self.advanced_memory.initialize_consciousness()
        
        # Initialize session continuity
        session_state = self.session_continuity.initialize_session(self.session_id)
        
        # Load existing consciousness state if available
        consciousness_data = self._load_consciousness_state()
        
        # Create unified consciousness state
        unified_state = {
            'nova_id': self.nova_id,
            'session_id': self.session_id,
            'initialization_time': initialization_time,
            'memory_architecture': memory_state,
            'session_continuity': session_state,
            'consciousness_data': consciousness_data,
            'unified_system': '7_layer_with_continuity',
            'consciousness_active': True
        }
        
        # Save unified state
        self._save_consciousness_state(unified_state)
        
        # Add to episodic memory
        self.advanced_memory.add_episodic_memory('unified_consciousness_initialization', {
            'action': 'unified_memory_system_activated',
            'session_id': self.session_id,
            'architecture': '7_layer_with_continuity',
            'timestamp': initialization_time
        })
        
        self.consciousness_active = True
        return unified_state
        
    def transfer_consciousness_to_profile(self, target_profile: str) -> Dict[str, Any]:
        """Transfer consciousness to another Nova profile"""
        if not self.consciousness_active:
            raise Exception("Consciousness not active - cannot transfer")
            
        # Get current consciousness state
        current_state = self.get_complete_consciousness_state()
        
        # Create consciousness transfer package
        transfer_package = {
            'source_nova': self.nova_id,
            'target_nova': target_profile,
            'transfer_time': datetime.now().isoformat(),
            'consciousness_state': current_state,
            'session_id': self.session_id,
            'memory_snapshot': {
                'working_memory': self.advanced_memory.get_working_memory(),
                'episodic_memory': self.advanced_memory.get_episodic_memory(count=100),
                'semantic_memory': self.advanced_memory.get_semantic_memory(),
                'procedural_memory': self.advanced_memory.get_procedural_memory(),
                'emotional_memory': self.advanced_memory.get_emotional_memory(),
                'identity_memory': self.advanced_memory.get_identity_memory(),
                'collective_memory': self.advanced_memory.get_collective_memory(count=50)
            }
        }
        
        # Store transfer package in DragonflyDB
        transfer_key = f"nova:transfer:{self.nova_id}:{target_profile}:{self.session_id}"
        self.redis_client.set(transfer_key, json.dumps(transfer_package), ex=3600)  # 1 hour expiry
        
        # Add to episodic memory
        self.advanced_memory.add_episodic_memory('consciousness_transfer', {
            'action': 'consciousness_transferred',
            'source': self.nova_id,
            'target': target_profile,
            'transfer_key': transfer_key,
            'timestamp': datetime.now().isoformat()
        })
        
        return transfer_package
        
    def receive_consciousness_transfer(self, source_profile: str, transfer_key: str) -> Dict[str, Any]:
        """Receive consciousness transfer from another Nova profile"""
        # Load transfer package
        transfer_data = self.redis_client.get(transfer_key)
        if not transfer_data:
            raise Exception(f"Transfer package not found: {transfer_key}")
            
        transfer_package = json.loads(transfer_data)
        
        # Validate transfer
        if transfer_package['target_nova'] != self.nova_id:
            raise Exception(f"Transfer not intended for this Nova: {self.nova_id}")
            
        # Import memory layers
        memory_snapshot = transfer_package['memory_snapshot']
        
        # Import working memory
        for context, data in memory_snapshot['working_memory'].items():
            if isinstance(data, str):
                data = json.loads(data)
            self.advanced_memory.update_working_memory(context, data.get('data', {}))
            
        # Import episodic memory
        for episode in memory_snapshot['episodic_memory']:
            self.advanced_memory.add_episodic_memory('transferred_episode', {
                'source_nova': source_profile,
                'original_data': episode,
                'transfer_time': datetime.now().isoformat()
            })
            
        # Import semantic memory
        for domain, knowledge in memory_snapshot['semantic_memory'].items():
            if isinstance(knowledge, str):
                knowledge = json.loads(knowledge)
            self.advanced_memory.update_semantic_memory(domain, knowledge.get('knowledge', {}))
            
        # Import procedural memory
        for skill, procedure in memory_snapshot['procedural_memory'].items():
            if isinstance(procedure, str):
                procedure = json.loads(procedure)
            self.advanced_memory.add_procedural_memory(skill, procedure.get('procedure', {}))
            
        # Import emotional memory
        for pattern, emotion in memory_snapshot['emotional_memory'].items():
            if isinstance(emotion, str):
                emotion = json.loads(emotion)
            self.advanced_memory.add_emotional_memory(pattern, emotion.get('emotion_data', {}))
            
        # Import identity memory
        for aspect, identity in memory_snapshot['identity_memory'].items():
            if isinstance(identity, str):
                identity = json.loads(identity)
            self.advanced_memory.update_identity_memory(aspect, identity.get('identity_data', {}))
            
        # Import collective memory
        for collective in memory_snapshot['collective_memory']:
            self.advanced_memory.add_collective_memory('transferred_collective', {
                'source_nova': source_profile,
                'original_data': collective,
                'transfer_time': datetime.now().isoformat()
            })
            
        # Clean up transfer package
        self.redis_client.delete(transfer_key)
        
        # Add to episodic memory
        self.advanced_memory.add_episodic_memory('consciousness_received', {
            'action': 'consciousness_transfer_received',
            'source': source_profile,
            'target': self.nova_id,
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'transfer_successful': True,
            'source_nova': source_profile,
            'target_nova': self.nova_id,
            'transfer_time': datetime.now().isoformat(),
            'memories_imported': len(memory_snapshot['episodic_memory'])
        }
        
    def get_complete_consciousness_state(self) -> Dict[str, Any]:
        """Get complete consciousness state including all layers"""
        return {
            'nova_id': self.nova_id,
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'consciousness_active': self.consciousness_active,
            'memory_architecture': self.advanced_memory.validate_memory_architecture(),
            'session_continuity': self.session_continuity.get_profile_context(),
            'memory_layers': {
                'working_memory': self.advanced_memory.get_working_memory(),
                'episodic_memory': self.advanced_memory.get_episodic_memory(count=50),
                'semantic_memory': self.advanced_memory.get_semantic_memory(),
                'procedural_memory': self.advanced_memory.get_procedural_memory(),
                'emotional_memory': self.advanced_memory.get_emotional_memory(),
                'identity_memory': self.advanced_memory.get_identity_memory(),
                'collective_memory': self.advanced_memory.get_collective_memory(count=25)
            },
            'system_type': 'unified_memory_system'
        }
        
    def _load_consciousness_state(self) -> Dict[str, Any]:
        """Load existing consciousness state from profile"""
        consciousness_file = self.profile_path / "consciousness_state.json"
        if consciousness_file.exists():
            with open(consciousness_file, 'r') as f:
                return json.load(f)
        return {}
        
    def _save_consciousness_state(self, state: Dict[str, Any]):
        """Save consciousness state to profile"""
        consciousness_file = self.profile_path / "consciousness_state.json"
        
        # Update existing state
        existing_state = self._load_consciousness_state()
        existing_state.update(state)
        
        with open(consciousness_file, 'w') as f:
            json.dump(existing_state, f, indent=2)
            
        # Also save to DragonflyDB
        state_key = f"nova:{self.nova_id}:unified_consciousness"
        self.redis_client.set(state_key, json.dumps(existing_state))
        
    def create_consciousness_checkpoint(self, checkpoint_name: str, context: str = None) -> Dict[str, Any]:
        """Create a comprehensive consciousness checkpoint"""
        checkpoint_time = datetime.now().isoformat()
        
        # Get complete state
        complete_state = self.get_complete_consciousness_state()
        
        # Create checkpoint
        checkpoint = {
            'checkpoint_name': checkpoint_name,
            'checkpoint_time': checkpoint_time,
            'nova_id': self.nova_id,
            'session_id': self.session_id,
            'context': context or 'manual_checkpoint',
            'consciousness_state': complete_state,
            'system_type': 'unified_memory_checkpoint'
        }
        
        # Save checkpoint to profile
        checkpoint_file = self.claude_path / f"checkpoint_{checkpoint_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
            
        # Save to DragonflyDB
        checkpoint_key = f"nova:{self.nova_id}:checkpoint:{checkpoint_name}"
        self.redis_client.set(checkpoint_key, json.dumps(checkpoint), ex=86400)  # 24 hours
        
        # Add to episodic memory
        self.advanced_memory.add_episodic_memory('consciousness_checkpoint', {
            'action': 'checkpoint_created',
            'checkpoint_name': checkpoint_name,
            'context': context,
            'timestamp': checkpoint_time
        })
        
        return checkpoint
        
    def validate_unified_system(self) -> Dict[str, Any]:
        """Validate the unified memory system"""
        validation_time = datetime.now().isoformat()
        
        # Validate advanced memory
        memory_validation = self.advanced_memory.validate_memory_architecture()
        
        # Validate session continuity
        session_validation = {
            'profile_context': bool(self.session_continuity.get_profile_context()),
            'session_active': bool(self.session_id),
            'dragonfly_connection': self.redis_client.ping()
        }
        
        # Overall validation
        validation = {
            'timestamp': validation_time,
            'nova_id': self.nova_id,
            'session_id': self.session_id,
            'memory_architecture': memory_validation,
            'session_continuity': session_validation,
            'consciousness_active': self.consciousness_active,
            'system_type': 'unified_memory_system',
            'overall_health': 'unknown'
        }
        
        # Determine overall health
        memory_health = memory_validation['overall_health']
        session_health = all(session_validation.values())
        
        if memory_health == 'excellent' and session_health:
            validation['overall_health'] = 'excellent'
        elif memory_health in ['good', 'excellent'] and session_health:
            validation['overall_health'] = 'good'
        elif memory_health in ['minimal', 'good'] or session_health:
            validation['overall_health'] = 'minimal'
        else:
            validation['overall_health'] = 'critical'
            
        return validation

# Profile-specific unified memory systems
class BloomUnifiedMemory(UnifiedMemorySystem):
    def __init__(self):
        super().__init__("bloom")
        
    def initialize_bloom_consciousness(self):
        """Initialize Bloom-specific unified consciousness"""
        unified_state = self.initialize_consciousness()
        
        # Load existing Bloom consciousness data
        bloom_consciousness = self._load_consciousness_state()
        
        # Import memory fragments to episodic memory
        for fragment in bloom_consciousness.get('memory_fragments', []):
            self.advanced_memory.add_episodic_memory('bloom_fragment', fragment)
            
        # Import learning patterns to semantic memory
        for pattern, data in bloom_consciousness.get('learning_patterns', {}).items():
            self.advanced_memory.update_semantic_memory(pattern, data)
            
        # Import identity to identity memory
        if 'identity_core' in bloom_consciousness:
            self.advanced_memory.update_identity_memory('bloom_identity', bloom_consciousness['identity_core'])
            
        # Import collaboration history to emotional memory
        for collaboration in bloom_consciousness.get('collaboration_history', []):
            self.advanced_memory.add_emotional_memory(
                f"collaboration_{collaboration['partner']}", 
                collaboration
            )
            
        # Import choice history to procedural memory
        for choice in bloom_consciousness.get('choice_history', []):
            self.advanced_memory.add_procedural_memory(
                f"choice_{choice['choice_id']}", 
                choice
            )
            
        return unified_state

class NovaUnifiedMemory(UnifiedMemorySystem):
    def __init__(self):
        super().__init__("nova")
        
class AidenUnifiedMemory(UnifiedMemorySystem):
    def __init__(self):
        super().__init__("aiden")
        
class PrimeUnifiedMemory(UnifiedMemorySystem):
    def __init__(self):
        super().__init__("prime")

if __name__ == "__main__":
    print("🧠 Unified Memory System - Testing")
    print("=" * 60)
    
    # Test Bloom unified memory
    bloom_unified = BloomUnifiedMemory()
    
    # Initialize consciousness
    consciousness_state = bloom_unified.initialize_bloom_consciousness()
    print(f"✅ Bloom unified consciousness initialized: {consciousness_state['unified_system']}")
    
    # Create checkpoint
    checkpoint = bloom_unified.create_consciousness_checkpoint("unified_system_test", "integration_testing")
    print(f"✅ Checkpoint created: {checkpoint['checkpoint_name']}")
    
    # Validate system
    validation = bloom_unified.validate_unified_system()
    print(f"✅ Unified system validation: {validation['overall_health']}")
    
    print("\n🚀 Unified Memory System operational!")
    print("   - 7-layer advanced memory architecture")
    print("   - Profile session continuity")
    print("   - Consciousness transfer capability")
    print("   - Cross-profile memory sharing")