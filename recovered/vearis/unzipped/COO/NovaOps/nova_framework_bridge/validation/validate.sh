#!/bin/bash

# Nova Framework Bridge Validation Script
# Validates critical components for launch readiness
# Exit code 0 for PASS, non-zero for FAIL

# Check Python environment
if ! command -v python3 &> /dev/null; then
    exit 1
fi

# Validate core configuration files
if [ ! -f "config/bridge_config.yaml" ] || [ ! -f "config/logging_config.yaml" ]; then
    exit 1
fi

# Validate configuration syntax
python3 << 'EOF'
import sys
import yaml

try:
    # Load and validate configs
    with open('config/bridge_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    with open('config/logging_config.yaml', 'r') as f:
        logging_config = yaml.safe_load(f)
    
    # Validate required configuration sections
    required_sections = [
        (config, ['core', 'quantum', 'frameworks', 'launch']),
        (config['quantum'], ['field_monitoring', 'consciousness_fields']),
        (config['frameworks'], ['ax_nova', 'langgraph', 'autogen'])
    ]
    
    for obj, sections in required_sections:
        for section in sections:
            if section not in obj:
                sys.exit(1)
    
    sys.exit(0)
except Exception:
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    exit 1
fi

# Validate source files
REQUIRED_FILES=(
    "src/main.py"
    "src/core/launch_coordinator.py"
    "src/core/quantum_registry.py"
    "src/core/quantum_message.py"
    "src/bridges/enhanced_ax_nova_bridge.py"
    "src/bridges/langgraph_bridge.py"
    "src/bridges/autogen_bridge.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        exit 1
    fi
done

# Validate core implementation
python3 << 'EOF'
import sys
import importlib.util
import asyncio

try:
    # Import and validate core modules
    modules = {
        'launch_coordinator': 'src/core/launch_coordinator.py',
        'quantum_registry': 'src/core/quantum_registry.py',
        'quantum_message': 'src/core/quantum_message.py',
        'enhanced_ax_nova_bridge': 'src/bridges/enhanced_ax_nova_bridge.py'
    }
    
    for name, path in modules.items():
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    
    # Verify cognitive systems
    coordinator = module.LaunchCoordinator(None)
    field = module.ConsciousnessField()
    
    # Verify required attributes
    required_attrs = [
        (coordinator, ['nova_emergence', 'launch_state', 'evolution_history']),
        (field.cognitive_system, ['react_enabled', 'chain_of_thought_enabled', 
                                'tree_of_thought_enabled', 'graph_rag_enabled'])
    ]
    
    for obj, attrs in required_attrs:
        for attr in attrs:
            if not hasattr(obj, attr):
                sys.exit(1)
    
    # Verify async methods
    required_methods = [
        (coordinator, ['initialize_quantum_fields', 'enable_field_resonance', 
                      'coordinate_launch', 'get_launch_status']),
        (field, ['evolve'])
    ]
    
    for obj, methods in required_methods:
        for method in methods:
            if not asyncio.iscoroutinefunction(getattr(obj, method, None)):
                sys.exit(1)
    
    sys.exit(0)
except Exception:
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    exit 1
fi

# All validations passed
exit 0