# Sohail-Agent-CLI Documentation

This document consolidates all usage, setup, and developer guidelines.

---

## Setup and Usage
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

# Plan a new project
sohail-agent plan "Build an ecommerce platform"

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

### `plan`

Interactively clarify a new project idea and create a persistent planning package.

```bash
sohail-agent plan "Build an ecommerce platform"

# Optional display name and output directory
sohail-agent plan "Build an ecommerce platform" \
  --project-name shopfront \
  --output ./project-plan
```

**Generates:**

- `project-plan/TASK.md`
- `project-plan/ARCHITECTURE.md`
- `project-plan/REQUIREMENTS.md`
- confirmed decision records under `project-plan/decisions/`

PlanningAgent V1 is deterministic and does not use Ollama, write application code,
run shell commands, or bootstrap the project. It records unresolved choices as open
questions rather than selecting hidden defaults.

Global options must appear before the subcommand:

```bash
sohail-agent --dry-run plan "Build an ecommerce platform"
sohail-agent --overwrite plan "Build an ecommerce platform"
```

Existing planning files are protected by default. With `--overwrite`, only
`TASK.md`, `ARCHITECTURE.md`, and `REQUIREMENTS.md` may be replaced. Existing
decision records are never overwritten by PlanningAgent V1.


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


---

# Sohail-Agent-CLI Developer Guide

## Architecture Rule

Preserve the existing style:

```text
CLI → Agent → Generator → Domain/Core Package
```

Do not rewrite existing agents to adopt new infrastructure unless a task explicitly asks for that integration.

## PlanningAgent

- Purpose: convert a project idea into persistent planning memory.
- Execution Flow: CLI `plan` → `PlanningAgent` → `PlanningGenerator` → `FileWorker`.
- Input: project goal and interactive answers.
- Output: `project-plan/TASK.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md`, and `decisions/`.
- CLI Command: `sohail-agent plan "Build ecommerce platform"`.
- Important Classes: `PlanningAgent`, `PlanningGenerator`, planning dataclasses.
- Tests: `tests/planning/`, `tests/agents/test_planning_agent.py`, `tests/generators/test_planning_generator.py`, `tests/test_cli_plan.py`.
- Extension Points: non-interactive answer input, decision updates, future specification consumption.

## BootstrapAgent

- Purpose: create a broad repository scaffold from a planning package.
- Execution Flow: CLI `bootstrap` → `BootstrapAgent` → `BootstrapGenerator` → `src/bootstrap`.
- Input: `project-plan/`.
- Output: repository folders and placeholder project files.
- CLI Command: `sohail-agent bootstrap --plan-dir ./project-plan --output ./generated`.
- Important Classes: `BootstrapAgent`, `BootstrapGenerator`, `PlanningLoader`, `PlanningValidator`, `ProjectScaffold`.
- Extension Points: consume structured plan details after contracts stabilize.

## StackAgent

- Purpose: generate technology-specific skeletons from PlanningAgent stack decisions.
- Execution Flow: CLI `stack` → `StackAgent` → `StackGenerator` → `src/stack`.
- Input: `project-plan/`.
- Output: frontend/backend/database skeleton files.
- CLI Command: `sohail-agent stack --plan-dir ./project-plan --output ./generated`.
- Important Classes: `StackAgent`, `StackGenerator`, `StackPlanLoader`, `StackSelector`, `StackProjectWriter`.
- Tests: `tests/stack/`, `tests/agents/test_stack_agent.py`, `tests/generators/test_stack_generator.py`, `tests/test_cli_stack.py`.
- Extension Points: additional supported stacks, richer project templates, framework-specific validation.

## AI Foundation

- Purpose: provide controlled reusable AI orchestration for future agents.
- Execution Flow: future agent → `AIOrchestrator` → route → prompt → provider → validate → parse → dataclass result.
- Input: `AIRequest`, optional `ProjectContext`.
- Output: `AIResult` containing `AIStructuredOutput` and `AIExecutionMetadata`.
- CLI Command: none; this is infrastructure.
- Important Classes: `AIContextBuilder`, `ProjectMemory`, `PromptCatalog`, `PromptBuilder`, `AIProviderFactory`, `AIRouter`, `AIOrchestrator`, `AIResponseValidator`, `AIResponseParser`.
- Tests: `tests/ai/`, `tests/providers/test_mock_provider.py`.
- Dependencies: existing provider layer, especially `MockProvider` and `OllamaProvider`.
- Future Extension Points: SpecificationAgent, BlueprintAgent, FeatureAgent, domain-specific AI dataclasses.

## Existing DevOps Agents

- Purpose: inspect repositories and generate DevOps/documentation assets.
- Execution Flow: CLI command → specific agent → analyzer/generator → FileWorker.
- Commands: `inspect`, `dockerize`, `k8s`, `cicd`, `docs`, `interview`, `all`.
- Important Classes: `RepoInspectorAgent`, `DockerAgent`, `K8sAgent`, `CicdAgent`, `DocsAgent`, `InterviewAgent`.
- Extension Points: V2 agents can consume planning and AI foundation outputs after contracts are explicit.

## AI Code Inventory

### `src/ai/__init__.py`

Purpose: exports AI foundation public classes.

Used By: future agents and tests.

Returns: package-level imports only.

### `src/ai/models.py`

Purpose: defines AI dataclasses.

Used By: orchestrator, prompts, parser, context builder.

Returns: `ProjectContext`, `AIRequest`, `AIResult`, and related dataclasses.

### `src/ai/context.py`

Purpose: builds normalized AI context from `project-plan/`.

Used By: future agents and memory construction.

Returns: `ProjectContext`.

### `src/ai/memory.py`

Purpose: stores serializable engineering memory.

Used By: future agents and context workflows.

Returns: `ProjectMemory`.

### `src/ai/prompts.py`

Purpose: owns reusable versioned prompts.

Used By: `AIOrchestrator`.

Returns: selected `PromptTemplate` and provider-ready prompt text.

### `src/ai/provider.py`

Purpose: selects Mock or Ollama provider; rejects cloud placeholders.

Used By: `AIOrchestrator`.

Returns: `BaseProvider`.

### `src/ai/registry.py`

Purpose: maps AI task names to prompt templates.

Used By: `AIRouter`.

Returns: `AIRoute`.

### `src/ai/router.py`

Purpose: attaches the right prompt name to an `AIRequest`.

Used By: `AIOrchestrator`.

Returns: routed `AIRequest`.

### `src/ai/orchestrator.py`

Purpose: controls prompt building, provider execution, validation, retry, and parsing.

Used By: future agents.

Returns: `AIResult`.

### `src/ai/response_parser.py`

Purpose: converts validated AI response data into dataclasses.

Used By: `AIOrchestrator`.

Returns: `AIStructuredOutput`.

### `src/ai/validator.py`

Purpose: rejects unsafe or malformed AI output.

Used By: `AIOrchestrator`.

Returns: validated JSON object for parser input.

### `src/ai/exceptions.py`

Purpose: central AI exception hierarchy.

Used By: all AI modules.

Returns: exceptions only.

## Validation Report

Commands executed during implementation:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/sohal/Documents/New\ project/Sohail-Agent-CLI-work \
  /Users/sohal/Documents/New\ project/Sohail-Agent-CLI-work/.test-venv/bin/python \
  -m pytest -q -p no:cacheprovider
```

Result:

```text
83 passed
```

Smoke coverage:

- Context builder loads PlanningAgent-style package.
- Mock provider executes deterministic responses.
- Orchestrator retries invalid JSON and returns dataclasses.
- Validator rejects empty, malformed, unknown-key, missing-field, enum, and type errors.

Known issues:

- Ollama network health was not smoke-tested.
- Cloud providers are placeholders by design.
