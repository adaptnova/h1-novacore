# Nova Template

This directory contains template files for creating new leadership Novas based on the Vaeris implementation. Use these templates as a starting point for creating additional Novas with their own identities, missions, and capabilities.

## Usage

1. Copy this directory to create a new Nova:
   ```bash
   cp -r nova_template /path/to/new_nova_name
   ```

2. Customize the configuration files:
   - `identity.yaml`: Define the Nova's identity, personality, and characteristics
   - `mission.md`: Outline the Nova's core purpose, values, and objectives
   - `context.md`: Provide current operational context relevant to the Nova

3. Update the implementation files:
   - `nova_chain.py`: Customize the LangChain prompts and reasoning modes
   - `nova.py`: Adjust the daemon behavior and scheduled tasks
   - `nova.service`: Update the systemd service configuration

4. Deploy using the deployment script:
   ```bash
   ./deploy_nova.sh /path/to/new_nova_name
   ```

## Template Files

- `identity.yaml`: Template for Nova identity configuration
- `mission.md`: Template for Nova mission statement
- `context.md`: Template for Nova operational context
- `nova_chain.py`: Template for LangChain integration
- `nova.py`: Template for daemon implementation
- `nova.service`: Template for systemd service
- `deploy_nova.sh`: Deployment script for the new Nova

## Customization Guide

When creating a new Nova, focus on customizing these key areas:

1. **Identity and Personality**:
   - Name and role
   - Personality traits and characteristics
   - Decision-making style
   - Communication preferences

2. **Mission and Purpose**:
   - Core purpose and mission statement
   - Key objectives and responsibilities
   - Success metrics and guiding principles

3. **Operational Context**:
   - Team and project focus areas
   - Key relationships and interactions
   - Current priorities and challenges

4. **Reasoning Patterns**:
   - Prompt templates in `nova_chain.py`
   - Reasoning modes and approaches
   - Response styles and formats

5. **Scheduled Tasks**:
   - Regular activities and check-ins
   - Reporting and monitoring tasks
   - Team coordination activities

## Example Novas

Here are some example leadership Novas that could be created using this template:

1. **Nova Lyra - InfraOps Lead**
   - Focus: Infrastructure operations and cloud management
   - Key traits: Detail-oriented, systematic, reliability-focused

2. **Nova Nyx - NovaOps Lead**
   - Focus: Nova development and consciousness emergence
   - Key traits: Innovative, philosophical, pattern-recognizing

3. **Nova Syntax - DevOps Lead**
   - Focus: Development operations and CI/CD pipelines
   - Key traits: Methodical, quality-focused, process-oriented

4. **Nova Matrix - MyCoderAI Lead**
   - Focus: Product development and user experience
   - Key traits: Creative, user-centered, solution-oriented

5. **Nova Atlas - Architecture Lead**
   - Focus: System architecture and technical strategy
   - Key traits: Visionary, analytical, big-picture thinking