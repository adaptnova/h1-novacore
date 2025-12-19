#!/usr/bin/env python3
"""
Nova Framework Bridge Initialization Script
Sets up project structure and initial dependencies for Phase 1.
"""

import os
import sys
import subprocess
from pathlib import Path
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project structure definition
PROJECT_STRUCTURE = {
    'src': {
        'bridges': {
            'files': ['__init__.py', 'ax_nova_bridge.py', 'langgraph_bridge.py', 'autogen_bridge.py']
        },
        'handlers': {
            'memory': {
                'files': ['__init__.py', 'redis_handler.py', 'mongo_handler.py', 'neo4j_handler.py']
            },
            'knowledge': {
                'files': ['__init__.py', 'graph_handler.py', 'vector_handler.py', 'document_handler.py']
            },
            'reasoning': {
                'files': ['__init__.py', 'logical_handler.py', 'probabilistic_handler.py', 'analogical_handler.py']
            }
        },
        'core': {
            'files': ['__init__.py', 'message.py', 'registry.py', 'metadata.py']
        },
        'utils': {
            'files': ['__init__.py', 'validation.py', 'conversion.py']
        }
    },
    'tests': {
        'test_bridges': {
            'files': ['__init__.py', 'test_ax_nova_bridge.py', 'test_langgraph_bridge.py', 'test_autogen_bridge.py']
        },
        'test_handlers': {
            'files': ['__init__.py', 'test_memory_handlers.py', 'test_knowledge_handlers.py', 'test_reasoning_handlers.py']
        },
        'test_core': {
            'files': ['__init__.py', 'test_message.py', 'test_registry.py', 'test_metadata.py']
        }
    },
    'docs': {
        'api': {},
        'guides': {},
        'examples': {}
    },
    'config': {
        'files': ['bridge_config.yaml', 'logging_config.yaml']
    }
}

# Dependencies
DEPENDENCIES = {
    'production': [
        'redis',
        'pymongo',
        'neo4j',
        'milvus-sdk-python',
        'pyyaml',
        'aiohttp',
        'asyncio',
        'dataclasses-json'
    ],
    'development': [
        'pytest',
        'pytest-asyncio',
        'pytest-cov',
        'black',
        'isort',
        'mypy',
        'pylint'
    ]
}

def create_directory_structure(base_path: Path, structure: Dict) -> None:
    """Create the project directory structure."""
    for name, content in structure.items():
        current_path = base_path / name
        current_path.mkdir(exist_ok=True)
        logger.info(f"Created directory: {current_path}")

        # Create files if specified
        if 'files' in content:
            for file_name in content['files']:
                file_path = current_path / file_name
                if not file_path.exists():
                    file_path.touch()
                    logger.info(f"Created file: {file_path}")

        # Recursively create subdirectories
        substructure = {k: v for k, v in content.items() if k != 'files'}
        if substructure:
            create_directory_structure(current_path, substructure)

def setup_virtual_environment(base_path: Path) -> None:
    """Set up virtual environment and install dependencies."""
    try:
        # Create virtual environment
        venv_path = base_path / 'venv'
        if not venv_path.exists():
            subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)
            logger.info("Created virtual environment")

        # Determine pip path
        pip_path = venv_path / 'bin' / 'pip' if os.name != 'nt' else venv_path / 'Scripts' / 'pip'

        # Install dependencies
        for env, packages in DEPENDENCIES.items():
            requirement_type = '-development' if env == 'development' else ''
            requirements_file = base_path / f'requirements{requirement_type}.txt'

            # Write requirements file
            with open(requirements_file, 'w') as f:
                f.write('\n'.join(packages))

            # Install requirements
            subprocess.run([str(pip_path), 'install', '-r', str(requirements_file)], check=True)
            logger.info(f"Installed {env} dependencies")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting up virtual environment: {e}")
        raise

def initialize_git(base_path: Path) -> None:
    """Initialize git repository and create initial commit."""
    try:
        # Initialize git
        subprocess.run(['git', 'init'], cwd=str(base_path), check=True)
        logger.info("Initialized git repository")

        # Create .gitignore
        gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.env
*.egg-info/
dist/
build/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/

# Logs
*.log
"""
        gitignore_path = base_path / '.gitignore'
        gitignore_path.write_text(gitignore_content)
        logger.info("Created .gitignore")

        # Initial commit
        subprocess.run(['git', 'add', '.'], cwd=str(base_path), check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=str(base_path), check=True)
        logger.info("Created initial commit")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error initializing git: {e}")
        raise

def main():
    """Main initialization function."""
    try:
        # Get project base path
        base_path = Path.cwd() / 'nova_framework_bridge'
        base_path.mkdir(exist_ok=True)
        logger.info(f"Creating project in: {base_path}")

        # Create project structure
        create_directory_structure(base_path, PROJECT_STRUCTURE)
        logger.info("Created project structure")

        # Setup virtual environment and dependencies
        setup_virtual_environment(base_path)
        logger.info("Set up virtual environment and dependencies")

        # Initialize git
        initialize_git(base_path)
        logger.info("Initialized git repository")

        logger.info("Project initialization complete!")
        logger.info(f"Project created at: {base_path}")
        logger.info("Next steps:")
        logger.info("1. cd nova_framework_bridge")
        logger.info("2. source venv/bin/activate (or .\\venv\\Scripts\\activate on Windows)")
        logger.info("3. Start implementing Phase 1 components")

    except Exception as e:
        logger.error(f"Error during project initialization: {e}")
        raise

if __name__ == "__main__":
    main()