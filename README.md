# Sohail-Agent-CLI

A local AI engineering assistant for DevOps, code generation, and repository automation.

## Overview

Sohail-Agent-CLI is a CLI-first tool that helps developers:

- **Inspect repositories** - Understand project structure, tech stack, and DevOps configuration
- **Generate Docker files** - Create production-minded Docker configurations
- **Generate Kubernetes manifests** - Create K8s deployment, service, and config files
- **Generate CI/CD pipelines** - Set up GitHub Actions workflows
- **Create documentation** - Generate professional README and deployment guides
- **Prepare for interviews** - Generate project summaries and talking points
- **Plan new projects** - Turn a project idea into persistent requirements, architecture, tasks, and decision records

## Why This Exists

Most AI coding tools are either:
- Cloud-dependent (sending your code to external APIs)
- Overly complex (trying to be "autonomous AGI")
- Hype-driven (making unrealistic claims)

Sohail-Agent-CLI is different:
- **Local-first** - Works with local AI models via Ollama
- **Transparent** - You see what it does, you control what it changes
- **Practical** - Solves real DevOps problems without overengineering
- **Modular** - Use only the parts you need

## Project Documentation

For a comprehensive understanding of the project, please refer to the following documentation files:

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Complete folder structure, high-level architecture, agent architecture, CLI flow, decision engine, planning engine, memory system, file generation system, component relationships, and design principles.
- **[DOCUMENTATION.md](DOCUMENTATION.md)**: Installation, setup, requirements, configuration, usage, CLI commands, examples, development workflow, testing, coding standards, and contribution guide.
- **[ROADMAP.md](ROADMAP.md)**: Current status, completed features, in progress, future features, long-term vision, and milestones.
- **[NOTES.md](NOTES.md)**: Developer notes, technical decisions, known limitations, bugs, ideas, and research notes.
- **[CHANGELOG.md](CHANGELOG.md)**: Version history and logical changes.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with Python 3.11+
- Uses Rich for terminal output
- Inspired by Ollama's clean API design
- Worker patterns inspired by lightweight execution frameworks

---

**Note:** This is a serious engineering tool. Generated files are starting points—always review and customize them for your specific needs.
