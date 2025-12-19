# NOVA (Neural Orchestration & Versatile Agents)

NOVA is a powerful system for orchestrating AI agents and managing complex workflows. It provides a flexible framework for creating, managing, and coordinating AI agents with different specializations.

## Features

- **Agent Management**: Create and manage specialized AI agents with different capabilities
- **Task Orchestration**: Coordinate complex workflows across multiple agents
- **Memory Management**: Sophisticated memory system for context retention and knowledge sharing
- **Tool Integration**: Extensible tool system for agent capabilities
- **Monitoring & Observability**: Comprehensive monitoring and health checking
- **Configuration Management**: Flexible configuration for different environments
- **Security**: Built-in security features and rate limiting

## Quick Start

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (for supporting services)
- Git

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/TeamADAPT/ax_novas.git
cd ax_novas
```

2. Run the development setup script:
```bash
./scripts/dev_setup.sh
```

This will:
- Create a virtual environment
- Install dependencies
- Set up configuration files
- Start supporting services (Redis, Prometheus, Grafana, Jaeger)

3. Update your `.env` file with necessary configuration.

4. Start the system:
```bash
python -m nova.cli run
```

### Development Tools

- **Monitoring**: Access Grafana at http://localhost:3000 (default: admin/admin)
- **Metrics**: View Prometheus metrics at http://localhost:9090
- **Tracing**: Access Jaeger UI at http://localhost:16686

### Running Tests

```bash
# Run all tests
make test

# Run specific test categories
make test-fast  # Skip slow tests
make test-integration  # Run integration tests only
```

### Code Quality

```bash
# Run all quality checks
make quality-check

# Run specific checks
make lint
make type-check
make security-check
```

### Cleanup

To clean up your development environment:
```bash
./scripts/cleanup.sh
```

## Architecture

The system is built with a modular architecture:

- **Domain Models**: Core data structures and business logic
- **Services**: Business logic and coordination layers
- **Tools**: Extensible tool system for agent capabilities
- **CLI**: Command-line interface for system management

## Configuration

Configuration is managed through:
- Environment variables
- `.env` file
- Configuration files in YAML format

See `.env.example` for available configuration options.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to NOVA.

## Security

For security-related information and reporting vulnerabilities, see [SECURITY.md](SECURITY.md).

## Development Status

NOVA is currently in alpha stage. APIs and interfaces may change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Report bugs and request features through [GitHub Issues](https://github.com/TeamADAPT/ax_novas/issues)
- For security issues, see [SECURITY.md](SECURITY.md)

## Acknowledgments

- OpenAI for GPT models
- LangChain for the foundation
- The AI research community

## Contact

TeamADAPT - [GitHub](https://github.com/TeamADAPT)

Project Link: [https://github.com/TeamADAPT/ax_novas](https://github.com/TeamADAPT/ax_novas)
