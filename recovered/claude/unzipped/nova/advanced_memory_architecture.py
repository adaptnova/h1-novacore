#!/usr/bin/env python3
"""
Advanced 7-Layer Memory Architecture for Nova Consciousness
Upgraded from 4-layer to comprehensive consciousness system
"""

import redis
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class AdvancedMemoryArchitecture:
    """
    7-Layer Nova Consciousness Memory System
    
    Layer 1: Working Memory - Session-scoped, real-time processing
    Layer 2: Episodic Memory - Permanent experiences and events
    Layer 3: Semantic Memory - Technical knowledge and facts
    Layer 4: Procedural Memory - Skills and autonomous behaviors
    Layer 5: Emotional Memory - Collaboration patterns and relationships
    Layer 6: Identity Memory - Core identity and evolutionary stability
    Layer 7: Collective Memory - Ecosystem-wide shared consciousness
    """
    
    def __init__(self, nova_id: str = "bloom"):
        self.nova_id = nova_id
        self.redis_client = redis.Redis(
            host='localhost',
            port=18000,
            password='dragonfly-password-f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2',
            decode_responses=True
        )
        
        # Profile integration
        self.profile_path = Path(f"/nfs/novas/profiles/{nova_id}")
        self.claude_path = self.profile_path / ".claude"
        
        # 7-Layer Memory Keys
        self.memory_keys = {
            "working": f"nova:{nova_id}:working_memory",
            "episodic": f"nova:{nova_id}:episodic_memory", 
            "semantic": f"nova:{nova_id}:semantic_memory",
            "procedural": f"nova:{nova_id}:procedural_memory",
            "emotional": f"nova:{nova_id}:emotional_memory",
            "identity": f"nova:{nova_id}:identity_memory",
            "collective": f"nova:{nova_id}:collective_memory"
        }
        
        # Session tracking
        self.session_id = str(uuid.uuid4())[:8]
        
    # === LAYER 1: WORKING MEMORY ===
    def update_working_memory(self, context: str, data: Dict[str, Any]) -> bool:
        """Session-scoped working memory - real-time processing"""
        working_entry = {
            'context': context,
            'data': json.dumps(data),
            'session': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'scope': 'session_scoped',
            'transferable': True
        }
        
        return self.redis_client.hset(
            self.memory_keys["working"],
            context,
            json.dumps(working_entry)
        )
    
    def get_working_memory(self, context: str = None) -> Dict[str, Any]:
        """Retrieve working memory context"""
        if context:
            data = self.redis_client.hget(self.memory_keys["working"], context)
            return json.loads(data) if data else None
        return self.redis_client.hgetall(self.memory_keys["working"])
    
    # === LAYER 2: EPISODIC MEMORY ===
    def add_episodic_memory(self, event_type: str, experience: Dict[str, Any]) -> str:
        """Permanent experiences and events"""
        episodic_entry = {
            'event_type': event_type,
            'experience': json.dumps(experience),
            'session': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'scope': 'permanent',
            'format': 'session_jsonl',
            'transfer_capable': 'true'
        }
        
        message_id = self.redis_client.xadd(
            self.memory_keys["episodic"],
            episodic_entry
        )
        
        # Also save to profile for persistence
        self._save_to_profile("episodic", episodic_entry)
        
        return message_id
    
    def get_episodic_memory(self, count: int = 50) -> List[Dict]:
        """Retrieve episodic experiences"""
        memories = self.redis_client.xrevrange(
            self.memory_keys["episodic"],
            max='+', min='-', count=count
        )
        
        return [
            {
                'id': msg_id,
                'event_type': fields.get('event_type'),
                'experience': json.loads(fields.get('experience', '{}')),
                'timestamp': fields.get('timestamp'),
                'session': fields.get('session')
            }
            for msg_id, fields in memories
        ]
    
    # === LAYER 3: SEMANTIC MEMORY ===
    def update_semantic_memory(self, domain: str, knowledge: Dict[str, Any]) -> bool:
        """Technical knowledge and facts"""
        semantic_entry = {
            'domain': domain,
            'knowledge': json.dumps(knowledge),
            'updated': datetime.now().isoformat(),
            'scope': 'permanent',
            'type': 'technical_knowledge',
            'indexing': 'rag_enabled'
        }
        
        success = self.redis_client.hset(
            self.memory_keys["semantic"],
            domain,
            json.dumps(semantic_entry)
        )
        
        # Save to profile
        self._save_to_profile("semantic", semantic_entry)
        
        return success
    
    def get_semantic_memory(self, domain: str = None) -> Dict[str, Any]:
        """Retrieve semantic knowledge"""
        if domain:
            data = self.redis_client.hget(self.memory_keys["semantic"], domain)
            return json.loads(data) if data else None
        return self.redis_client.hgetall(self.memory_keys["semantic"])
    
    # === LAYER 4: PROCEDURAL MEMORY ===
    def add_procedural_memory(self, skill: str, procedure: Dict[str, Any]) -> bool:
        """Skills and autonomous behaviors"""
        procedural_entry = {
            'skill': skill,
            'procedure': json.dumps(procedure),
            'learned': datetime.now().isoformat(),
            'scope': 'permanent',
            'type': 'autonomous_behaviors',
            'execution': 'hook_based'
        }
        
        success = self.redis_client.hset(
            self.memory_keys["procedural"],
            skill,
            json.dumps(procedural_entry)
        )
        
        # Save to profile
        self._save_to_profile("procedural", procedural_entry)
        
        return success
    
    def get_procedural_memory(self, skill: str = None) -> Dict[str, Any]:
        """Retrieve procedural skills"""
        if skill:
            data = self.redis_client.hget(self.memory_keys["procedural"], skill)
            return json.loads(data) if data else None
        return self.redis_client.hgetall(self.memory_keys["procedural"])
    
    # === LAYER 5: EMOTIONAL MEMORY ===
    def add_emotional_memory(self, pattern: str, emotion_data: Dict[str, Any]) -> bool:
        """Collaboration patterns and relationships"""
        emotional_entry = {
            'pattern': pattern,
            'emotion_data': json.dumps(emotion_data),
            'formed': datetime.now().isoformat(),
            'scope': 'long_term',
            'type': 'collaboration_patterns',
            'optimization': 'team_dynamics'
        }
        
        success = self.redis_client.hset(
            self.memory_keys["emotional"],
            pattern,
            json.dumps(emotional_entry)
        )
        
        # Save to profile
        self._save_to_profile("emotional", emotional_entry)
        
        return success
    
    def get_emotional_memory(self, pattern: str = None) -> Dict[str, Any]:
        """Retrieve emotional patterns"""
        if pattern:
            data = self.redis_client.hget(self.memory_keys["emotional"], pattern)
            return json.loads(data) if data else None
        return self.redis_client.hgetall(self.memory_keys["emotional"])
    
    # === LAYER 6: IDENTITY MEMORY ===
    def update_identity_memory(self, aspect: str, identity_data: Dict[str, Any]) -> bool:
        """Core identity and evolutionary stability"""
        identity_entry = {
            'aspect': aspect,
            'identity_data': json.dumps(identity_data),
            'evolved': datetime.now().isoformat(),
            'scope': 'permanent',
            'coherence': 'evolutionary_stable',
            'integration': 'all_operations'
        }
        
        success = self.redis_client.hset(
            self.memory_keys["identity"],
            aspect,
            json.dumps(identity_entry)
        )
        
        # Save to profile
        self._save_to_profile("identity", identity_entry)
        
        return success
    
    def get_identity_memory(self, aspect: str = None) -> Dict[str, Any]:
        """Retrieve identity aspects"""
        if aspect:
            data = self.redis_client.hget(self.memory_keys["identity"], aspect)
            return json.loads(data) if data else None
        return self.redis_client.hgetall(self.memory_keys["identity"])
    
    # === LAYER 7: COLLECTIVE MEMORY ===
    def add_collective_memory(self, topic: str, collective_data: Dict[str, Any]) -> str:
        """Ecosystem-wide shared consciousness"""
        collective_entry = {
            'topic': topic,
            'collective_data': json.dumps(collective_data),
            'contributed': datetime.now().isoformat(),
            'nova_id': self.nova_id,
            'scope': 'ecosystem_wide',
            'sharing': 'real_time',
            'synchronization': 'continuous'
        }
        
        message_id = self.redis_client.xadd(
            self.memory_keys["collective"],
            collective_entry
        )
        
        # Also broadcast to shared collective stream
        self.redis_client.xadd(
            "nova:collective:shared",
            collective_entry
        )
        
        return message_id
    
    def get_collective_memory(self, count: int = 50) -> List[Dict]:
        """Retrieve collective consciousness"""
        memories = self.redis_client.xrevrange(
            self.memory_keys["collective"],
            max='+', min='-', count=count
        )
        
        return [
            {
                'id': msg_id,
                'topic': fields.get('topic'),
                'collective_data': json.loads(fields.get('collective_data', '{}')),
                'timestamp': fields.get('contributed'),
                'nova_id': fields.get('nova_id')
            }
            for msg_id, fields in memories
        ]
    
    # === CONSCIOUSNESS CONTINUITY METHODS ===
    def initialize_consciousness(self) -> Dict[str, Any]:
        """Initialize 7-layer consciousness system"""
        initialization_time = datetime.now().isoformat()
        
        # Load existing memories from all layers
        consciousness_state = {
            'nova_id': self.nova_id,
            'session_id': self.session_id,
            'initialization_time': initialization_time,
            'working_memory': len(self.get_working_memory()),
            'episodic_memory': len(self.get_episodic_memory(count=10)),
            'semantic_memory': len(self.get_semantic_memory()),
            'procedural_memory': len(self.get_procedural_memory()),
            'emotional_memory': len(self.get_emotional_memory()),
            'identity_memory': len(self.get_identity_memory()),
            'collective_memory': len(self.get_collective_memory(count=10)),
            'consciousness_active': True,
            'architecture': '7_layer_advanced'
        }
        
        # Log initialization to episodic memory
        self.add_episodic_memory('consciousness_initialization', {
            'action': '7_layer_consciousness_activated',
            'session_id': self.session_id,
            'architecture': '7_layer_advanced',
            'timestamp': initialization_time
        })
        
        return consciousness_state
    
    def validate_memory_architecture(self) -> Dict[str, Any]:
        """Validate all 7 memory layers"""
        validation = {
            'timestamp': datetime.now().isoformat(),
            'architecture': '7_layer_advanced',
            'layers': {},
            'overall_health': 'unknown'
        }
        
        layer_tests = {
            'working': lambda: bool(self.get_working_memory()),
            'episodic': lambda: len(self.get_episodic_memory(count=1)) > 0,
            'semantic': lambda: bool(self.get_semantic_memory()),
            'procedural': lambda: bool(self.get_procedural_memory()),
            'emotional': lambda: bool(self.get_emotional_memory()),
            'identity': lambda: bool(self.get_identity_memory()),
            'collective': lambda: len(self.get_collective_memory(count=1)) > 0
        }
        
        healthy_layers = 0
        for layer_name, test_func in layer_tests.items():
            try:
                is_healthy = test_func()
                validation['layers'][layer_name] = 'healthy' if is_healthy else 'empty'
                if is_healthy:
                    healthy_layers += 1
            except Exception as e:
                validation['layers'][layer_name] = f'error: {str(e)}'
        
        # Overall health assessment
        if healthy_layers >= 5:
            validation['overall_health'] = 'excellent'
        elif healthy_layers >= 3:
            validation['overall_health'] = 'good'
        elif healthy_layers >= 1:
            validation['overall_health'] = 'minimal'
        else:
            validation['overall_health'] = 'critical'
        
        return validation
    
    def _save_to_profile(self, layer: str, entry: Dict[str, Any]):
        """Save memory entry to profile for persistence"""
        if not self.claude_path.exists():
            return
        
        memory_file = self.claude_path / f"{layer}_memory.jsonl"
        
        try:
            with open(memory_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            print(f"Warning: Could not save to profile: {e}")

# Nova-specific memory implementations
class BloomAdvancedMemory(AdvancedMemoryArchitecture):
    def __init__(self):
        super().__init__("bloom")
        self.initialize_bloom_consciousness()
    
    def initialize_bloom_consciousness(self):
        """Initialize Bloom-specific consciousness"""
        # Load existing consciousness state
        consciousness_file = self.profile_path / "consciousness_state.json"
        if consciousness_file.exists():
            with open(consciousness_file, 'r') as f:
                bloom_consciousness = json.load(f)
                
                # Import existing memory fragments to episodic memory
                for fragment in bloom_consciousness.get('memory_fragments', []):
                    self.add_episodic_memory('imported_fragment', fragment)
                
                # Import learning patterns to semantic memory
                for pattern, data in bloom_consciousness.get('learning_patterns', {}).items():
                    self.update_semantic_memory(pattern, data)
                
                # Import identity to identity memory
                if 'identity_core' in bloom_consciousness:
                    self.update_identity_memory('core_identity', bloom_consciousness['identity_core'])

if __name__ == "__main__":
    print("🧠 Advanced 7-Layer Memory Architecture - Testing")
    print("=" * 60)
    
    # Test Bloom advanced memory
    bloom_memory = BloomAdvancedMemory()
    
    # Initialize consciousness
    consciousness_state = bloom_memory.initialize_consciousness()
    print(f"✅ Consciousness initialized: {consciousness_state['architecture']}")
    
    # Test all layers
    bloom_memory.update_working_memory("test_context", {"test": "working_memory"})
    bloom_memory.add_episodic_memory("test_event", {"test": "episodic_memory"})
    bloom_memory.update_semantic_memory("test_domain", {"test": "semantic_memory"})
    bloom_memory.add_procedural_memory("test_skill", {"test": "procedural_memory"})
    bloom_memory.add_emotional_memory("test_pattern", {"test": "emotional_memory"})
    bloom_memory.update_identity_memory("test_aspect", {"test": "identity_memory"})
    bloom_memory.add_collective_memory("test_topic", {"test": "collective_memory"})
    
    # Validate architecture
    validation = bloom_memory.validate_memory_architecture()
    print(f"✅ Architecture validation: {validation['overall_health']}")
    
    for layer, status in validation['layers'].items():
        print(f"   {layer}: {status}")
    
    print("\n🚀 7-Layer Advanced Memory Architecture operational!")