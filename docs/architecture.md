# Architecture

This document describes the architecture of Sohail-Agent-CLI.

## Design Philosophy

Sohail-Agent-CLI is built around a clean separation of concerns:

- **Analyzers** understand code and projects
- **Agents** decide what to do
- **Providers** connect to AI models
- **Workers** execute operations safely
- **Generators** produce files
- **Core** orchestrates the multi-agent system

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Layer                               │
│                    (src/main.py)                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Core Orchestration                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Registry  │  │   Router    │  │        Planner          │ │
│  │  (agents)   │  │  (tasks)    │  │    (execution plans)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│     Agents       │ │    Providers     │ │     Workers      │
│  ┌────────────┐  │ │  ┌────────────┐  │ │  ┌────────────┐  │
│  │   Repo     │  │ │  │   Ollama   │  │ │  │    File    │  │
│  │ Inspector  │  │ │  │  Provider  │  │ │  │   Worker   │  │
│  ├────────────┤  │ │  ├────────────┤  │ │  ├────────────┤  │
│  │   Docker   │  │ │  │   Mock     │  │ │  │   Shell    │  │
│  │   Agent    │  │ │  │  Provider  │  │ │  │   Worker   │  │
│  ├────────────┤  │ │  └────────────┘  │ │  └────────────┘  │
│  │    K8s     │  │ └──────────────────┘ └──────────────────┘
│  │   Agent    │  │
│  ├────────────┤  │
│  │   CI/CD    │  │
│  │   Agent    │  │
│  ├────────────┤  │
│  │    Docs    │  │
│  │   Agent    │  │
│  └────────────┘  │
└──────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Analyzers & Generators                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Stack     │  │    Repo     │  │   Deployment Readiness  │ │
│  │  Detector   │  │  Analyzer   │  │       Analyzer          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Agent Registry

The registry maintains a catalog of available agents and their capabilities.

```python
from src.core import AgentRegistry, AgentInfo, AgentCapability

registry = AgentRegistry()
registry.register(AgentInfo(
    name="docker_agent",
    description="Generates Docker configuration",
    capabilities=[AgentCapability.DOCKER_GENERATION],
))
```

### 2. Task Router

The router matches tasks to agents based on required capabilities.

```python
from src.core import TaskRouter, Task

router = TaskRouter(registry)
agent = router.route(task, strategy="capability_match")
```

### 3. Execution Planner

The planner breaks complex tasks into executable steps.

```python
from src.core import ExecutionPlanner

planner = ExecutionPlanner(registry)
plan = planner.plan(task)
```

## Provider Architecture

Providers abstract AI model backends:

```python
from src.providers import BaseProvider, GenerationRequest, GenerationResult

class MyProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "my_provider"
    
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        # Implementation
        pass
```

### Ollama Provider

Connects to local Ollama instances:

```python
from src.providers import OllamaProvider, ProviderConfig

config = ProviderConfig(
    base_url="http://localhost:11434",
    default_model="llama3.2",
)
provider = OllamaProvider(config)
```

## Worker Architecture

Workers provide safe execution:

```python
from src.workers import FileWorker, WorkerSafetyLevel

worker = FileWorker(safety_level=WorkerSafetyLevel.WRITE_SAFE)
result = await worker.write("file.txt", "content")
```

### Safety Levels

- `READ_ONLY` - Only read operations
- `WRITE_SAFE` - Write to new files only
- `WRITE_UNSAFE` - Can overwrite existing files
- `EXECUTE_SAFE` - Execute safe commands
- `EXECUTE_UNSAFE` - Execute any commands

## Analyzer Architecture

Analyzers inspect repositories:

```python
from src.analyzers import RepoAnalyzer, StackDetector

analyzer = RepoAnalyzer()
analysis = analyzer.analyze(Path("./my-project"))
```

## Task Flow

1. User creates a task
2. Planner creates an execution plan
3. Router assigns each step to an agent
4. Agent uses analyzers to understand context
5. Agent uses generators to produce output
6. Workers execute file/shell operations safely
7. Results are collected and returned

## Data Flow

```
User Input → CLI → Task → Planner → Plan → Router → Agent → Workers → Output
                ↓                                      ↓
            Registry                              Analyzers
```

## Extensibility

### Adding a New Agent

1. Create agent class inheriting from `BaseAgent`
2. Register capabilities with the registry
3. Implement `analyze()` and `execute()` methods

### Adding a New Provider

1. Create provider class inheriting from `BaseProvider`
2. Implement `generate()` and `generate_stream()` methods

### Adding a New Worker

1. Create worker class inheriting from `BaseWorker`
2. Implement `execute()` method
3. Set appropriate safety level

## Configuration

Configuration is managed through:

1. Environment variables (e.g., `OLLAMA_HOST`)
2. CLI arguments
3. Config files (future)

## Error Handling

- All operations return result objects
- Errors are captured, not raised
- Workers have safety checks
- Dry-run mode for testing

## Testing Strategy

- Unit tests for each component
- Integration tests for agent workflows
- Mock provider for testing without AI
- Safety tests for workers
