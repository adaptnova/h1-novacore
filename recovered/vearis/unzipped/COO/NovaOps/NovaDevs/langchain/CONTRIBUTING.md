# Contributing to Nova LangChain Framework

## Semantic Versioning
We follow semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes, backward compatible

## Branch Strategy
- main: Production releases
- develop: Development branch
- feature/NOVA-{ticket}-description: Feature branches
- bugfix/NOVA-{ticket}-description: Bug fix branches
- enhancement/NOVA-{ticket}-description: Enhancement branches

## Commit Messages
Format: type(scope): NOVA-{ticket} description
Example: feat(agents): NOVA-123 Add new agent capability

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

## Pull Request Process
1. Create branch from main
2. Implement changes
3. Update documentation
4. Submit PR with description
5. Address review comments
6. Squash and merge

## Code Style
- Follow PEP 8
- Use type hints
- Write docstrings
- Include tests
