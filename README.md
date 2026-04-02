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

## Architecture

```
Sohail-Agent-CLI/
├── analyzers/      # Repository and stack analysis
├── agents/         # Task-specific agents
├── providers/      # AI model backends (Ollama, etc.)
├── workers/        # Safe execution layer
├── generators/     # File generation
├── core/           # Multi-agent orchestration
│   ├── registry.py    # Agent registry
│   ├── router.py      # Task routing
│   └── planner.py     # Execution planning
└── templates/      # Jinja2 templates
```

### Multi-Agent System

The tool uses a real multi-agent architecture:

1. **Agent Registry** - Maintains available agents and their capabilities
2. **Task Router** - Routes tasks to appropriate agents
3. **Execution Planner** - Breaks complex tasks into steps
4. **Providers** - AI model backends (Ollama integration)
5. **Workers** - Safe execution layer for file/shell operations

## Installation

```bash
# Clone the repository
git clone https://github.com/sohail-24/sohail-agent-cli.git
cd sohail-agent-cli

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### Requirements

- Python 3.11+
- Optional: Ollama for local AI features

## Quick Start

```bash
# Inspect a repository
sohail-agent inspect ./my-project

# Generate Docker configuration
sohail-agent dockerize ./my-project

# Generate Kubernetes manifests
sohail-agent k8s ./my-project

# Generate CI/CD workflows
sohail-agent cicd ./my-project

# Generate documentation
sohail-agent docs ./my-project

# Generate interview notes
sohail-agent interview ./my-project

# Run all agents
sohail-agent all ./my-project
```

## Commands

### `inspect`

Analyze repository structure, detect tech stack, and assess deployment readiness.

```bash
sohail-agent inspect [path]
```

**Output:**
- Technology stack detection
- DevOps files status
- Deployment readiness score (0-100)
- Gaps and recommendations

### `dockerize`

Generate Docker configuration for the detected stack.

```bash
sohail-agent dockerize [path]
```

**Generates:**
- `Dockerfile`
- `.dockerignore`
- `docker-compose.yml` (optional)

### `k8s`

Generate Kubernetes manifests.

```bash
sohail-agent k8s [path]
```

**Generates:**
- `k8s/deployment.yaml`
- `k8s/service.yaml`
- `k8s/kustomization.yaml`

### `cicd`

Generate GitHub Actions workflows.

```bash
sohail-agent cicd [path]
```

**Generates:**
- `.github/workflows/ci.yml`
- `.github/workflows/docker.yml`
- `.github/workflows/release.yml`

### `docs`

Generate project documentation.

```bash
sohail-agent docs [path]
```

**Generates:**
- `README.md`
- `DEPLOYMENT.md`

### `interview`

Generate interview-ready project summary.

```bash
sohail-agent interview [path]
```

**Generates:**
- `INTERVIEW_NOTES.md`

### `all`

Run all agents on the project.

```bash
sohail-agent all [path]
```

## Supported Stacks

| Stack | Inspect | Docker | K8s | CI/CD | Docs |
|-------|---------|--------|-----|-------|------|
| Python | ✅ | ✅ | ✅ | ✅ | ✅ |
| Django | ✅ | ✅ | ✅ | ✅ | ✅ |
| FastAPI | ✅ | ✅ | ✅ | ✅ | ✅ |
| Flask | ✅ | ✅ | ✅ | ✅ | ✅ |
| Node.js | ✅ | ✅ | ✅ | ✅ | ✅ |
| React | ✅ | ✅ | ✅ | ✅ | ✅ |
| Next.js | ✅ | ✅ | ✅ | ✅ | ✅ |
| Vue | ✅ | ✅ | ✅ | ✅ | ✅ |
| Go | ✅ | ✅ | ✅ | ✅ | ✅ |
| Rust | ✅ | ✅ | ✅ | ✅ | ✅ |
| Java | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ruby/Rails | ✅ | ✅ | ✅ | ✅ | ✅ |
| PHP/Laravel | ✅ | ✅ | ✅ | ✅ | ✅ |

## Ollama Integration

The tool can use local AI models via Ollama for enhanced generation:

```python
from src.providers import OllamaProvider, ProviderConfig

config = ProviderConfig(
    base_url="http://localhost:11434",
    default_model="llama3.2",
)

provider = OllamaProvider(config)
```

### Setting up Ollama

1. Install Ollama: https://ollama.com
2. Pull a model: `ollama pull llama3.2`
3. The tool will automatically use Ollama when available

## Provider Architecture

Providers abstract AI model backends:

```python
from src.providers import BaseProvider, GenerationRequest

class MyProvider(BaseProvider):
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        # Implementation
        pass
```

Built-in providers:
- `OllamaProvider` - Local models via Ollama
- `MockProvider` - Testing without API calls

## Worker Architecture

Workers provide safe execution of operations:

```python
from src.workers import FileWorker, ShellWorker, WorkerSafetyLevel

# Safe file operations
file_worker = FileWorker(safety_level=WorkerSafetyLevel.WRITE_SAFE)
result = await file_worker.write("file.txt", "content")

# Safe shell execution
shell_worker = ShellWorker(safety_level=WorkerSafetyLevel.EXECUTE_SAFE)
result = await shell_worker.run("git status")
```

## Safety Features

- **Dry-run mode** - See what would change without making changes
- **Safety levels** - Control what operations are allowed
- **File overwrite protection** - Never overwrite without permission
- **Blocked commands** - Dangerous shell commands are blocked

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=src tests/
```

## Project Structure

```
Sohail-Agent-CLI/
├── src/
│   ├── analyzers/      # Stack detection, repo analysis
│   ├── agents/         # Task-specific agents
│   ├── providers/      # AI model backends
│   ├── workers/        # Safe execution layer
│   ├── generators/     # File generation
│   ├── core/           # Multi-agent orchestration
│   ├── templates/      # Jinja2 templates
│   └── utils/          # Shared utilities
├── tests/              # Test suite
├── docs/               # Documentation
└── examples/           # Example outputs
```

## Roadmap

### v2.1.0
- [ ] Full agent implementations (Docker, K8s, CI/CD, Docs)
- [ ] Template system with Jinja2
- [ ] More stack support (Elixir, Scala, Kotlin)

### v2.2.0
- [ ] Enhanced Ollama integration
- [ ] Streaming responses
- [ ] Interactive mode

### v2.3.0
- [ ] Plugin system
- [ ] Custom agent support
- [ ] Configuration files

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with Python 3.11+
- Uses Rich for terminal output
- Inspired by Ollama's clean API design
- Worker patterns inspired by lightweight execution frameworks

---

**Note:** This is a serious engineering tool. Generated files are starting points—always review and customize them for your specific needs.
