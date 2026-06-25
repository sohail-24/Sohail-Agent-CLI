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
