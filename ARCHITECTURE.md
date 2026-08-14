# Sohail-Agent-CLI Architecture

This document consolidates all architecture documentation for Sohail-Agent-CLI.

---

## High-Level Architecture (from README)

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


---

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


---

# PlanningAgent Design

## Document Status

- **Status:** Proposed
- **Project stage:** Early V1
- **Design scope:** PlanningAgent and its persistent planning artifacts
- **Implementation status:** Not implemented
- **Primary constraint:** Additive design that preserves all existing commands and the current `CLI → Agent → Analyzer → Generator → Worker` execution model

This document designs PlanningAgent from the current repository state described in `PROJECT-AUDIT.md`, `PROJECT-NOTES.md`, `docs/architecture.md`, and the source under `src/`.

The design deliberately does not treat the existing `AgentRegistry`, `TaskRouter`, or `ExecutionPlanner` as an active runtime. They are currently isolated core components, while `src/main.py` directly dispatches commands to agents. PlanningAgent V1 should follow the working runtime pattern and must not force a repository-wide orchestration rewrite.

# Section 1 — What PlanningAgent Is

## Definition

PlanningAgent is an interactive project-discovery and planning agent that converts an incomplete project idea into a small, persistent, human-readable planning package.

Example input:

`sohail-agent plan "Build an ecommerce platform"`

Example output:

```text
project-plan/
├── TASK.md
├── ARCHITECTURE.md
├── REQUIREMENTS.md
└── decisions/
    ├── 001_frontend.md
    ├── 002_backend.md
    ├── 003_database.md
    └── 004_deployment.md
```

PlanningAgent is not a code generator, repository bootstrapper, autonomous implementation agent, or replacement for the existing core `ExecutionPlanner`.

Its product responsibility is:

> Turn user intent and explicit decisions into durable planning documents that humans can review and future commands can consume.

## Why It Should Exist

The current agents begin with an existing repository and generate or inspect technical artifacts. They do not solve the earlier problem: deciding what should be built before a repository exists.

PlanningAgent fills that gap:

- captures ambiguous project intent;
- asks a bounded set of clarification questions;
- records choices and unresolved questions;
- produces requirements, architecture, and task breakdowns;
- stores decisions as files rather than temporary chat context;
- creates a stable handoff point for future commands such as `bootstrap`;
- keeps project planning local and version-controllable.

This is a natural extension of Sohail-Agent-CLI because the project is already:

- CLI-first;
- local-first;
- agent-oriented;
- focused on engineering workflows;
- built around generating reviewable files;
- explicitly opposed to opaque or uncontrolled autonomy.

## How It Improves Sohail-Agent-CLI

PlanningAgent gives the tool a useful “before code exists” workflow while preserving its practical identity.

It would improve the product in four ways:

1. **Continuity**

   User decisions survive beyond one terminal session.

2. **Traceability**

   Requirements, architecture choices, and tasks can refer to stable IDs.

3. **Human review**

   Generated plans are ordinary Markdown files that can be edited, reviewed, committed, and discussed.

4. **Future command interoperability**

   A future `bootstrap` command can read explicit decisions instead of guessing a stack from a one-line prompt.

## How It Differs From Existing Agents

| Agent | Starting point | Primary output | Executes infrastructure/code? |
|---|---|---|---|
| Repo Inspector Agent | Existing repository | Console analysis | No |
| Docker Agent | Existing repository | Docker files | Writes files |
| Kubernetes Agent | Existing repository | Kubernetes manifests | Writes files |
| CI/CD Agent | Existing repository | GitHub Actions workflows | Writes files |
| Docs Agent | Existing repository | README and deployment docs | Writes files |
| Interview Agent | Existing repository | Interview notes | Writes files |
| **PlanningAgent** | Project idea, optionally an existing repository | Requirements, architecture, tasks, decisions | Writes planning files only |

PlanningAgent differs in two important architectural ways:

- it gathers structured user input before generation;
- its output is intended to become persistent project memory, not a one-time generated artifact.

## PlanningAgent Versus `ExecutionPlanner`

The names are close but the responsibilities are different.

### PlanningAgent

- plans the user’s software project;
- asks product and architecture questions;
- creates persistent Markdown artifacts;
- operates at project-design time;
- is user-facing.

### Existing `ExecutionPlanner`

- creates in-memory `ExecutionPlan` and `PlanStep` objects;
- describes how agents could execute CLI tasks;
- operates at agent-orchestration time;
- currently has no executor and is unused by the CLI.

PlanningAgent V1 should not be built on top of `ExecutionPlanner`. Doing so would mix project planning with unfinished runtime orchestration and would expand the implementation scope unnecessarily.

# Section 2 — Current Architecture Analysis

## Current Active Architecture

The implemented runtime is:

```text
CLI command
    ↓
direct command function in src/main.py
    ↓
specific agent
    ↓
analyzer, when repository context is needed
    ↓
generator or template logic
    ↓
BaseAgent.write_file()
    ↓
FileWorker
```

PlanningAgent should initially fit this real path:

```text
CLI
    ↓
PlanningAgent
    ↓
Question/answer model
    ↓
Planning document generator
    ↓
FileWorker
```

For planning an existing repository, `RepoAnalyzer` may provide optional context:

```text
CLI
    ↓
PlanningAgent
    ├── user goal and answers
    └── optional RepoAnalyzer facts
            ↓
Planning document generator
            ↓
FileWorker
```

## BaseAgent

### Reusable

PlanningAgent can reuse:

- agent identity through `name` and `description`;
- `dry_run` and `verbose` state;
- Rich-based `info`, `success`, `warning`, and `error` output;
- `write_file()` as the route to `FileWorker`;
- `AgentResult` as the public agent result type, after baseline result semantics are corrected.

### Necessary Caution

The current `BaseAgent.write_file()` interface returns a tuple and existing agents often report success after failed or skipped writes. PlanningAgent must not copy that behavior.

Before implementation, the project should define truthful output semantics:

- created;
- updated;
- skipped because a file exists;
- dry-run previewed;
- failed.

PlanningAgent creates persistent memory. Misreporting a skipped or failed write would be especially harmful because a later command could assume the plan exists when it does not.

### Recommendation

Keep `BaseAgent` unchanged for the design phase. PlanningAgent should conform to it in V1. Any improvement to result semantics should be a general baseline hardening change applied consistently across all agents, not a PlanningAgent-only workaround.

## RepoAnalyzer

### Reusable

`RepoAnalyzer` can be useful when the user runs planning against an existing repository. It can supply:

- repository name;
- detected primary and secondary stack;
- entry points;
- key dependencies;
- project structure summary;
- presence of Docker, CI/CD, Kubernetes, tests, and documentation.

### Not Required for Greenfield V1

For `plan "Build an ecommerce platform"`, there may be no repository to analyze. PlanningAgent must work from the goal and answers alone.

### Reliability Boundary

RepoAnalyzer output is heuristic and should be treated as observed context, not an accepted design decision.

Planning documents must distinguish:

- **Detected fact:** “A `package.json` containing React dependencies was found.”
- **User decision:** “Next.js will be used for the frontend.”
- **Agent suggestion:** “Next.js may simplify server rendering.”
- **Unresolved question:** “Hosting platform has not been selected.”

PlanningAgent must never silently convert analyzer confidence into an accepted architecture choice.

### Recommendation

- V1: no dependency on RepoAnalyzer for greenfield planning.
- V2: optional repository-aware mode.
- Future: reconcile plan decisions against repository reality and report drift.

## Router

`TaskRouter` currently routes `Task` metadata to `AgentInfo` metadata. It does not hold or invoke live agent instances, and the CLI does not use it.

### V1 Position

Leave it unchanged and unused by PlanningAgent.

The `plan` command should be dispatched directly from `src/main.py`, matching every current command. This minimizes risk and keeps PlanningAgent independent from unfinished orchestration.

### Later Potential

After the router is tested and connected to actual agent execution, PlanningAgent could advertise a project-planning capability and be routed like other agents.

That integration is V2 or later, not a V1 prerequisite.

## Planner

The existing `ExecutionPlanner` produces runtime steps such as repository analysis followed by Docker generation. It does not generate product requirements or architecture decisions.

### V1 Position

Do not modify it for PlanningAgent V1.

Do not add project tasks from `TASK.md` directly to `PlanStep`. The concepts differ:

- `TASK.md` tasks are user-project work items that may take days or weeks.
- `PlanStep` values are intended to be immediate agent execution steps.

### Later Potential

A future bootstrap workflow could translate eligible `TASK.md` items into runtime tasks, but that must be an explicit adapter with validation. The Markdown task model should not be forced into the current `PlanStep` model.

## Registry

`AgentRegistry` stores `AgentInfo` and capability metadata but is not initialized with current agents.

### V1 Position

Leave it unchanged.

PlanningAgent should not be the first agent registered while every existing agent remains directly dispatched. That would create two inconsistent execution models.

### Later Potential

After core integration is deliberately completed, add a project-planning capability and register PlanningAgent alongside all existing agents.

## Providers

### Reusable

`BaseProvider`, `OllamaProvider`, `GenerationRequest`, and `MockProvider` provide a reasonable starting point for optional language synthesis.

Suitable PlanningAgent provider uses include:

- rewriting structured answers into clear prose;
- summarizing the project goal;
- explaining accepted architecture decisions;
- improving task descriptions;
- suggesting alternatives for the user to choose from.

### Provider Boundary

Providers must not be authoritative for:

- selecting the final stack;
- accepting a decision without user confirmation;
- inventing requirements;
- resolving conflicts silently;
- marking tasks complete;
- executing shell commands;
- creating code or infrastructure in the planning command.

The structured answers and accepted decision records are the source of truth. AI-generated prose is a presentation layer.

### V1 Recommendation

PlanningAgent V1 should work without Ollama.

If Ollama is included in the first implementation, it must be optional and must have deterministic fallback behavior. `MockProvider` should be used in tests through provider injection rather than direct construction of `OllamaProvider`.

## Workers

### FileWorker

PlanningAgent should use `FileWorker` through the existing `BaseAgent.write_file()` path.

The planning directory should be the only write target. No file outside the selected output root should be touched.

Required behaviors:

- no overwrite by default;
- dry-run lists every planned file;
- partial failures produce a failed or partial result, never unconditional success;
- directory creation is performed through the file-writing path;
- future update operations preserve decision history.

The current `base_path` behavior is not a reliable containment boundary. Path confinement should be hardened before PlanningAgent accepts user-controlled output paths.

### ShellWorker

PlanningAgent must not use `ShellWorker`.

Planning is a document-generation workflow. It does not need to:

- install dependencies;
- initialize Git;
- create application source;
- run package managers;
- execute Docker;
- invoke Kubernetes;
- inspect the system through shell commands.

Avoiding shell execution keeps PlanningAgent safely bounded and prevents “planning” from becoming hidden implementation.

## Existing Components That Should Remain Unchanged

PlanningAgent V1 should not require changes to the behavior of:

- Docker Agent;
- Kubernetes Agent;
- CI/CD Agent;
- Docs Agent;
- Interview Agent;
- existing analyzers;
- `TaskRouter`;
- `ExecutionPlanner`;
- `AgentRegistry`;
- `ShellWorker`;
- existing generator output formats.

Only additive integration should be necessary after baseline hardening:

- a new command;
- a new agent;
- planning-specific data models;
- a planning document generator;
- exports and tests;
- documentation.

# Section 3 — PlanningAgent Responsibilities

## Responsibility Principles

PlanningAgent should:

- ask before assuming;
- record unknowns rather than fabricate answers;
- preserve the user’s wording where important;
- separate facts, decisions, suggestions, and unresolved questions;
- produce deterministic structure;
- remain useful without an AI provider;
- stop at planning artifacts.

PlanningAgent should not:

- write application code;
- generate Docker/Kubernetes/CI files;
- execute shell commands;
- initialize repositories;
- install packages;
- choose technologies without confirmation;
- claim architectural certainty when inputs are incomplete;
- create an autonomous agent chain.

## V1 Responsibilities

V1 should be intentionally small.

### 1. Project Discovery

Capture:

- project name;
- one-sentence goal;
- target users;
- primary problem;
- first-release scope;
- explicit out-of-scope items.

### 2. Bounded Clarification Questions

Ask a predictable set of questions based on the project category.

For a web application, the first question set may cover:

- frontend approach;
- backend approach;
- database;
- authentication;
- deployment target;
- Docker requirement;
- Kubernetes requirement;
- initial scale or traffic expectation.

V1 should ask no more than approximately 5–10 required questions in one session. Optional questions can be skipped and recorded as unresolved.

### 3. Requirements Gathering

Convert answers into:

- functional requirements;
- non-functional requirements;
- constraints;
- assumptions;
- out-of-scope statements;
- open questions.

### 4. Architecture Planning

Create a high-level architecture consistent with accepted decisions.

V1 architecture should remain conceptual:

- components;
- responsibilities;
- data flow;
- external systems;
- deployment direction;
- security considerations;
- unresolved architecture questions.

It should not invent low-level code structure or exact cloud resources unless the user explicitly decided them.

### 5. Task Breakdown

Produce an ordered, traceable implementation backlog.

Tasks should:

- have stable IDs;
- have statuses;
- have priorities;
- declare dependencies;
- link to requirements and decisions;
- describe completion criteria;
- avoid code-level micromanagement.

### 6. Decision Tracking

Create one decision record per confirmed, consequential choice.

Examples:

- frontend framework;
- backend framework;
- database;
- authentication model;
- deployment model.

### 7. Safe File Generation

Write only:

- `project-plan/TASK.md`;
- `project-plan/ARCHITECTURE.md`;
- `project-plan/REQUIREMENTS.md`;
- accepted/proposed records under `project-plan/decisions/`.

## V2 Responsibilities

V2 may add controlled evolution of existing plans.

### 1. Resume and Update

- read an existing `project-plan/`;
- ask only questions affected by the requested change;
- update derived documents;
- preserve accepted decision history;
- create superseding decision records instead of rewriting history.

### 2. Existing Repository Context

- use `RepoAnalyzer` to compare implementation with the plan;
- label detected facts separately from planned decisions;
- report drift such as “Plan says PostgreSQL; repository contains MongoDB configuration.”

### 3. Optional Ollama Synthesis

- improve prose while preserving structured facts;
- summarize trade-offs;
- suggest candidate alternatives;
- generate draft rationale for explicit user approval.

### 4. Plan Validation

Detect:

- missing required decisions;
- circular task dependencies;
- task references to missing requirements;
- architecture choices without decision records;
- conflicting requirements;
- stale or superseded decisions still referenced.

### 5. Controlled Change History

Add a small change log or metadata field showing when planning files were last regenerated and which decision caused the change.

## Future Vision

Future capabilities should remain downstream consumers of the planning package.

### Future `bootstrap`

`bootstrap` could:

- read accepted decisions;
- validate required fields;
- show a proposed scaffold plan;
- require confirmation;
- invoke deterministic generators;
- write source or infrastructure only through safe workers.

### Future Planning Drift

An existing repository could be checked against:

- requirements;
- accepted decisions;
- planned components;
- planned deployment model.

### Future Multi-Agent Integration

After the core registry/router/planner has a tested executor:

- PlanningAgent can be registered;
- bootstrap steps can be routed to appropriate agents;
- plan artifacts can become explicit inputs to agent tasks;
- results can update task status only after user-approved execution.

### Explicitly Excluded Future Direction

The future vision does not require:

- autonomous swarms;
- self-modifying plans;
- hidden vector memory;
- background implementation;
- cloud dashboards;
- planning agents recursively creating other agents;
- automatic production deployment.

# Section 4 — Folder Structure

## Proposed Structure

```text
project-plan/
├── TASK.md
├── ARCHITECTURE.md
├── REQUIREMENTS.md
└── decisions/
    ├── 001_frontend.md
    ├── 002_backend.md
    ├── 003_database.md
    ├── 004_authentication.md
    └── 005_deployment.md
```

V1 should not add caches, databases, hidden state, generated JSON mirrors, vector stores, or session transcripts.

## `TASK.md`

### Purpose

The implementation backlog and current execution state.

### Owns

- task IDs;
- task descriptions;
- status;
- priority;
- dependencies;
- owner;
- linked requirements;
- linked decisions;
- acceptance criteria;
- notes.

### Does Not Own

- architecture rationale;
- complete requirement definitions;
- final technical decisions.

Those belong in `ARCHITECTURE.md`, `REQUIREMENTS.md`, and `decisions/`.

## `ARCHITECTURE.md`

### Purpose

The current high-level technical design.

### Owns

- system context;
- component boundaries;
- major data flows;
- deployment view;
- security and reliability direction;
- architecture assumptions;
- links to accepted decisions.

### Does Not Own

- decision history;
- detailed implementation backlog;
- product acceptance criteria.

## `REQUIREMENTS.md`

### Purpose

The scope contract for what the project should do and the qualities it must have.

### Owns

- functional requirements;
- non-functional requirements;
- constraints;
- assumptions;
- out-of-scope items;
- open questions;
- acceptance criteria.

### Does Not Own

- technology rationale;
- task status;
- implementation details.

## `decisions/`

### Purpose

Append-oriented, durable architecture and product decision memory.

### Owns

- decision context;
- selected option;
- rationale;
- alternatives;
- consequences;
- status and supersession.

## Source-of-Truth Precedence

When documents conflict, use this order:

1. accepted decision records for explicit choices;
2. `REQUIREMENTS.md` for agreed scope and constraints;
3. `ARCHITECTURE.md` for the current derived system design;
4. `TASK.md` for work sequencing.

If an accepted decision changes, the correct lifecycle is:

1. create a new decision record;
2. mark the old decision as superseded;
3. update requirements if scope changed;
4. update architecture;
5. update affected tasks.

## Ownership Model

### User

The user owns final decisions, scope, priorities, and acceptance.

### PlanningAgent

PlanningAgent owns:

- asking questions;
- creating structured drafts;
- maintaining cross-references;
- identifying conflicts and unknowns;
- writing files after confirmation.

PlanningAgent does not own product authority.

### Future Bootstrap Command

Bootstrap owns consumption of accepted planning artifacts. It must not rewrite decisions to make execution easier.

## Update Lifecycle

### Initial Creation

- planning directory does not exist;
- PlanningAgent asks questions;
- user confirms a summary;
- all artifacts are generated as one logical operation;
- partial write failure is reported clearly.

### Human Editing

Files remain ordinary Markdown and may be edited manually. Stable IDs and headings should make manual edits safe.

### V2 Update

- existing files are parsed;
- the requested change is identified;
- affected decisions are proposed;
- user confirms;
- new decision records are appended;
- derived documents are updated;
- unrelated content is preserved.

### Deletion

PlanningAgent should not automatically delete accepted decision records. Obsolete decisions are marked superseded or rejected.

# Section 5 — `TASK.md` Format

## Design Goals

`TASK.md` must be:

- readable in a terminal or GitHub;
- manually editable;
- stable enough for future parsing;
- traceable to requirements and decisions;
- simple enough to avoid becoming a project-management product.

## Recommended Structure

```markdown
---
planning_schema: 1
project: shopfront
document: tasks
status: active
updated: 2026-06-24
---

# Task Plan

## Status Definitions

- `proposed`
- `ready`
- `in_progress`
- `blocked`
- `done`
- `cancelled`

## Priority Definitions

- `P0` — required for the first usable release
- `P1` — important after the core path works
- `P2` — valuable but deferrable
- `P3` — optional

## Task Summary

| ID | Task | Status | Priority | Depends On | Owner |
|---|---|---|---|---|---|
| T-001 | Establish application skeleton | ready | P0 | — | unassigned |
| T-002 | Implement product catalog | proposed | P0 | T-001 | backend |
| T-003 | Implement storefront | proposed | P0 | T-001, T-002 | frontend |

## T-001 — Establish Application Skeleton

- **Status:** ready
- **Priority:** P0
- **Owner:** unassigned
- **Dependencies:** none
- **Requirements:** FR-001, NFR-002
- **Decisions:** DEC-001, DEC-002

### Objective

Create the initial frontend and backend application boundaries defined in the architecture.

### Acceptance Criteria

- frontend and backend can run independently;
- local configuration is documented;
- no production deployment is included in this task.

### Notes

- keep deployment work separate in T-008;
- authentication is not part of this task.
```

## Required Fields

Every task must contain:

- **ID:** stable `T-NNN` identifier;
- **Title:** short action-oriented description;
- **Status:** one of the defined states;
- **Priority:** `P0`–`P3`;
- **Owner:** a person, role, team, `unassigned`, or `user`;
- **Dependencies:** task IDs or `none`;
- **Requirements:** linked requirement IDs;
- **Decisions:** linked decision IDs when relevant;
- **Objective:** outcome, not implementation trivia;
- **Acceptance Criteria:** evidence that the task is complete;
- **Notes:** risks, exclusions, or useful context.

## Status Lifecycle

```text
proposed → ready → in_progress → done
                   ↘ blocked ↗

proposed/ready/in_progress → cancelled
```

PlanningAgent V1 should create tasks primarily as `proposed` or `ready`.

PlanningAgent must not mark implementation tasks `done`. Only a human or a future verified execution workflow should do that.

## Dependency Rules

- dependencies use task IDs only;
- unknown dependencies are not allowed;
- circular dependencies are invalid;
- a task should not be `ready` while a required dependency is incomplete;
- tasks may refer to multiple requirements and decisions.

## Realistic Example

```markdown
## T-006 — Implement Checkout

- **Status:** proposed
- **Priority:** P0
- **Owner:** backend
- **Dependencies:** T-002, T-004, T-005
- **Requirements:** FR-008, FR-009, NFR-004
- **Decisions:** DEC-003, DEC-004

### Objective

Allow an authenticated customer to create an order from the current cart using the selected payment-provider integration.

### Acceptance Criteria

- stock is validated before order creation;
- payment success creates one confirmed order;
- payment failure does not confirm the order;
- duplicate payment callbacks are handled idempotently;
- secrets are not stored in source control.

### Notes

- refunds are outside the first release;
- guest checkout remains unresolved in OQ-002.
```

# Section 6 — Decision Memory System

## Goal

The `decisions/` directory is the durable memory of consequential choices.

It should answer:

- what was decided;
- why it was decided;
- what alternatives were considered;
- what consequences were accepted;
- whether the decision is still current.

The design should follow a lightweight Architecture Decision Record pattern without requiring formal ADR tooling.

## Naming Convention

```text
NNN_short_slug.md
```

Examples:

- `001_frontend.md`
- `002_backend.md`
- `003_database.md`
- `004_authentication.md`
- `005_deployment.md`

Rules:

- three-digit, monotonically increasing number;
- lowercase slug;
- words separated by underscores;
- never renumber existing decisions;
- filename number is creation order, not priority;
- one primary decision topic per file.

## Decision Identifier

Inside the document, use:

`DEC-NNN`

Example:

- filename: `003_database.md`
- identifier: `DEC-003`

## Recommended Format

```markdown
---
planning_schema: 1
id: DEC-003
title: Select the primary database
status: accepted
date: 2026-06-24
supersedes: null
superseded_by: null
---

# DEC-003 — Select the Primary Database

## Context

The first release requires customer accounts, products, inventory, carts, orders, and payment records. These records have transactional relationships and must remain consistent during checkout.

## Decision

Use PostgreSQL as the primary transactional database.

## Rationale

- the domain is relational;
- checkout requires transactions;
- uniqueness and foreign-key constraints are valuable;
- PostgreSQL has mature operational tooling.

## Alternatives Considered

### MongoDB

Rejected for the primary store because the core order and payment model benefits from relational constraints and transactions.

### SQLite

Suitable for local prototypes but not selected as the production database.

## Consequences

### Positive

- strong transactional guarantees;
- clear relational data model;
- broad hosting support.

### Negative

- schema migrations must be managed;
- production backups and connection limits must be planned.

## Related Requirements

- FR-003
- FR-008
- NFR-004

## Related Tasks

- T-002
- T-006

## Open Questions

- managed provider is not selected;
- retention period is not defined.
```

## Decision Statuses

- **proposed:** draft awaiting explicit confirmation;
- **accepted:** current authoritative decision;
- **rejected:** considered and not selected;
- **superseded:** replaced by a later decision;
- **deprecated:** still present but planned for removal.

## Lifecycle

### Creation

PlanningAgent drafts a proposed decision from the conversation.

### Confirmation

The user confirms or changes the decision. Only then may it become `accepted`.

### Change

Accepted decisions are not rewritten to hide history.

If the database changes from PostgreSQL to MongoDB:

1. create a new decision record;
2. set the old record to `superseded`;
3. set `superseded_by` on the old record;
4. set `supersedes` on the new record;
5. update architecture, requirements, and affected tasks.

### Rejection

A proposed option may be kept as `rejected` when its rationale is useful. Trivial unselected options do not need separate files; they can remain under “Alternatives Considered.”

## Memory Rules

- decision files are the authoritative record for accepted technical choices;
- model-generated suggestions are not decisions;
- user answers must be confirmed before acceptance;
- unresolved topics remain open questions, not invented defaults;
- sensitive values, secrets, passwords, and tokens must never be stored;
- decision history is append-oriented;
- decision documents should remain concise.

# Section 7 — `ARCHITECTURE.md` Design

## Purpose

`ARCHITECTURE.md` is the current high-level design derived from accepted decisions and requirements.

It explains the intended system without requiring a reader to reconstruct it from every decision record.

## Recommended Sections

1. **Document Metadata**
   - schema version;
   - project;
   - status;
   - last updated;
   - referenced decision IDs.

2. **Architecture Summary**
   - one-paragraph system description.

3. **Goals and Non-Goals**
   - what the design optimizes for;
   - what it intentionally does not cover.

4. **System Context**
   - users;
   - external services;
   - system boundary.

5. **Major Components**
   - frontend;
   - backend/API;
   - database;
   - background workers, if accepted;
   - external integrations.

6. **Component Responsibilities**
   - one clear responsibility list per component.

7. **Data Flow**
   - important request and event paths;
   - no invented low-level implementation details.

8. **Data Model Overview**
   - major entities and relationships;
   - link to database decision.

9. **Authentication and Authorization**
   - selected model;
   - trust boundaries;
   - unresolved security decisions.

10. **Deployment View**
    - local development;
    - intended production shape;
    - Docker/Kubernetes only when explicitly selected.

11. **Reliability and Observability**
    - error handling direction;
    - logging;
    - monitoring;
    - backup/recovery expectations.

12. **Security and Privacy**
    - sensitive data;
    - secrets;
    - data retention;
    - known constraints.

13. **Architecture Decisions**
    - index of accepted decision records.

14. **Assumptions and Open Questions**
    - clearly unresolved topics.

## Example Outline

```markdown
# Architecture

## Summary

Shopfront is a web application with a Next.js frontend, a Python API, and PostgreSQL as the transactional data store.

## Major Components

### Web Frontend

- renders catalog, cart, checkout, and account screens;
- communicates with the backend API;
- does not access the database directly.

### Backend API

- owns business rules;
- validates authentication and authorization;
- coordinates inventory, orders, and payments.

### PostgreSQL

- stores users, products, inventory, carts, orders, and payment references;
- is the system of record for transactional state.

## Decision Index

- [DEC-001 — Frontend](decisions/001_frontend.md)
- [DEC-002 — Backend](decisions/002_backend.md)
- [DEC-003 — Database](decisions/003_database.md)
```

## Future Usage

`ARCHITECTURE.md` can later be consumed by:

- `bootstrap` to understand component boundaries;
- Docs Agent to produce accurate documentation;
- Interview Agent to explain architecture without inventing claims;
- Repo Inspector to compare planned and detected architecture;
- human reviewers during design and implementation.

Future commands must treat it as a current view, not the full decision history.

# Section 8 — `REQUIREMENTS.md` Design

## Purpose

`REQUIREMENTS.md` defines what the project must accomplish, how well it must operate, and what constraints apply.

It is the scope contract between the idea and the implementation plan.

## Requirement Categories

### Functional Requirements

Functional requirements describe user-visible or system behavior.

Identifier:

`FR-NNN`

Examples:

- `FR-001`: A visitor can browse active products.
- `FR-002`: A customer can add products to a cart.
- `FR-003`: A customer can create an account.
- `FR-004`: An authenticated customer can place an order.
- `FR-005`: An administrator can update product inventory.

### Non-Functional Requirements

Non-functional requirements describe quality attributes.

Identifier:

`NFR-NNN`

Examples:

- `NFR-001`: The main catalog page should meet the agreed response-time target.
- `NFR-002`: Secrets must be provided through runtime configuration.
- `NFR-003`: Checkout operations must be idempotent.
- `NFR-004`: Order creation must preserve transactional consistency.
- `NFR-005`: Production errors must be logged without exposing sensitive data.

### Constraints

Constraints describe fixed boundaries or mandated choices.

Identifier:

`CON-NNN`

Examples:

- `CON-001`: The first release must run locally with Docker Compose.
- `CON-002`: The project must use only locally hosted AI during planning.
- `CON-003`: The initial team has one frontend and one backend developer.
- `CON-004`: Kubernetes is outside the first release.

## Recommended Structure

```markdown
---
planning_schema: 1
project: shopfront
document: requirements
status: draft
updated: 2026-06-24
---

# Requirements

## Project Goal

Build a small ecommerce platform for a single merchant.

## Target Users

- shoppers;
- authenticated customers;
- store administrators.

## Functional Requirements

### FR-001 — Browse Products

- **Priority:** must
- **Status:** accepted
- **Source:** user
- **Acceptance:** Visitors can view active products with name, image, price, and stock state.

### FR-002 — Manage Cart

- **Priority:** must
- **Status:** accepted
- **Source:** user
- **Acceptance:** A visitor can add, update, and remove cart items.

## Non-Functional Requirements

### NFR-001 — Secret Management

- **Priority:** must
- **Status:** accepted
- **Acceptance:** No production secret is committed to source control.

## Constraints

### CON-001 — Initial Deployment

The first release will use Docker Compose and will not require Kubernetes.

## Assumptions

- one merchant owns the catalog;
- one currency is supported initially.

## Out of Scope

- marketplace sellers;
- multiple warehouses;
- native mobile applications;
- recommendation engines.

## Open Questions

- OQ-001: Is guest checkout required?
- OQ-002: Which payment provider will be used?
```

## Requirement Fields

Each requirement should include:

- stable ID;
- title;
- category;
- priority;
- status;
- source;
- requirement statement;
- acceptance criterion;
- related decision IDs, when applicable;
- notes or open questions.

## Requirement Statuses

- proposed;
- accepted;
- deferred;
- rejected;
- superseded.

## Priority Vocabulary

Use a small vocabulary:

- must;
- should;
- could;
- will_not.

This is easier to understand in requirements than reusing task priority labels.

## Constraints Versus Decisions

The distinction matters:

- “The organization mandates PostgreSQL” is a constraint.
- “PostgreSQL was selected after comparing alternatives” is a decision.

A topic may appear in both files when a decision satisfies a constraint, but the documents should link rather than duplicate full rationale.

# Section 9 — Execution Flow

## V1 User Flow

```text
User
  ↓
plan command with project goal
  ↓
PlanningAgent validates goal and output path
  ↓
PlanningAgent selects a bounded question set
  ↓
User answers or skips questions
  ↓
PlanningAgent normalizes answers
  ↓
PlanningAgent shows summary, decisions, and open questions
  ↓
User confirms
  ↓
Planning document generator creates in-memory content
  ↓
FileWorker writes project-plan files
  ↓
PlanningAgent reports created, skipped, dry-run, and failed files
```

## Initial Planning Sequence

```mermaid
sequenceDiagram
    actor User
    participant CLI as CLI (src/main.py)
    participant Agent as PlanningAgent
    participant Questions as Question Catalog
    participant Provider as Optional Provider
    participant Generator as Planning Generator
    participant Worker as FileWorker
    participant Files as project-plan/

    User->>CLI: plan "Build an ecommerce platform"
    CLI->>Agent: execute(goal, output_path, dry_run, overwrite)
    Agent->>Questions: select questions for project category

    loop Required clarification
        Questions-->>Agent: next question
        Agent-->>User: ask bounded question
        User-->>Agent: answer or skip
    end

    Agent->>Agent: normalize answers and identify open questions

    opt Ollama enabled and healthy
        Agent->>Provider: synthesize prose from structured facts
        Provider-->>Agent: draft prose
    end

    Agent-->>User: show plan summary and proposed decisions
    User-->>Agent: confirm
    Agent->>Generator: generate requirements, architecture, tasks, decisions
    Generator-->>Agent: file-content map

    loop Each planning artifact
        Agent->>Worker: write(path, content)
        Worker-->>Agent: created, skipped, dry-run, or failed
    end

    Agent-->>CLI: AgentResult
    CLI-->>User: final status and file list
```

## Important Flow Rules

### Confirmation Boundary

No decision becomes `accepted` and no file is written until the user confirms the normalized summary.

### Skip Behavior

If the user skips a required planning choice:

- the topic is recorded as an open question;
- no default is silently accepted;
- dependent tasks may be marked blocked or proposed;
- future bootstrap must refuse affected actions until resolved.

### Dry-Run Behavior

Dry-run should:

- conduct the question flow;
- produce the normalized summary;
- show target files;
- optionally show concise content summaries;
- perform no writes.

Provider/network behavior in dry-run must be explicitly documented. The safer default is deterministic generation without provider calls unless the user explicitly requested AI enhancement.

### Overwrite Behavior

For initial V1:

- existing planning files are protected by default;
- `--overwrite` may replace generated summary documents only after a clear warning;
- accepted decision records should not be silently replaced;
- if any protected decision file conflicts, the operation should stop or skip with a non-success result.

For V2 updates, a dedicated update lifecycle is preferable to broad overwrite.

## V2 Update Sequence

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant Agent as PlanningAgent
    participant Reader as Plan Reader/Validator
    participant Analyzer as Optional RepoAnalyzer
    participant Generator as Planning Generator
    participant Worker as FileWorker

    User->>CLI: plan --update "Switch deployment to Kubernetes"
    CLI->>Agent: update request
    Agent->>Reader: read existing planning package
    Reader-->>Agent: parsed requirements, architecture, tasks, decisions

    opt Existing repository supplied
        Agent->>Analyzer: analyze repository
        Analyzer-->>Agent: detected implementation facts
    end

    Agent-->>User: ask change-specific questions
    User-->>Agent: confirm new decision
    Agent->>Generator: create superseding decision and derived updates
    Generator-->>Agent: changed file-content map
    Agent-->>User: preview affected files
    User-->>Agent: approve write

    loop Changed artifacts
        Agent->>Worker: safely write approved update
        Worker-->>Agent: result
    end

    Agent-->>User: report new decision and updated references
```

## Future Bootstrap Sequence

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant Bootstrap as Bootstrap Command
    participant Plan as Plan Reader/Validator
    participant Core as Future Orchestration Core
    participant Agents as Existing Generating Agents
    participant Worker as Safe Workers

    User->>CLI: bootstrap
    CLI->>Bootstrap: start
    Bootstrap->>Plan: read and validate project-plan/
    Plan-->>Bootstrap: accepted decisions, requirements, ready tasks

    alt Required decisions unresolved
        Bootstrap-->>User: stop with blocking questions
    else Plan valid
        Bootstrap-->>User: show proposed execution plan
        User-->>Bootstrap: confirm
        Bootstrap->>Core: create validated execution tasks
        Core->>Agents: route deterministic generation work
        Agents->>Worker: write approved files
        Worker-->>Agents: results
        Agents-->>Core: task results
        Core-->>Bootstrap: execution summary
        Bootstrap-->>User: report outputs and failures
    end
```

# Section 10 — Integration Strategy

## CLI Integration

### V1 Command Shape

Conceptual interface:

```text
sohail-agent plan "Build an ecommerce platform"
```

Potential bounded options:

- output root;
- project name;
- non-interactive answers file, later;
- optional Ollama use;
- dry-run;
- overwrite for initial documents only.

The command should follow the current direct dispatch model:

```text
main.py command map
    ↓
cmd_plan()
    ↓
PlanningAgent.execute()
```

Do not route only this command through `TaskRouter` while existing commands remain direct.

### Interactive Input

V1 may use ordinary terminal prompts. The question engine should be separate from the agent’s document-rendering logic so it can later support:

- interactive CLI;
- pre-supplied answers;
- tests;
- resumed sessions.

### Non-Interactive Environments

V1 should detect when required input cannot be collected. It should fail with a clear message rather than hang in CI or redirected input.

## Agent Integration

PlanningAgent should inherit from `BaseAgent` to remain consistent with existing agents.

Its conceptual internal collaborators are:

- a question catalog or discovery component;
- planning-specific data models;
- a planning document generator;
- optional `BaseProvider`;
- `FileWorker` through the base write path.

The agent should coordinate; it should not contain all Markdown templates inline. The current Interview Agent shows the maintenance cost of embedding a large template directly in an agent.

## Generator Integration

Planning documents deserve a dedicated deterministic generator.

The generator should accept structured planning data and return a file-content map, conceptually:

```text
TASK.md → content
ARCHITECTURE.md → content
REQUIREMENTS.md → content
decisions/001_frontend.md → content
...
```

The generator must not:

- ask questions;
- call providers;
- write files;
- execute commands;
- infer accepted decisions from missing data.

This preserves the existing Analyzer/Generator/Worker separation even though greenfield planning may not need an analyzer.

## Core Integration

### V1

No runtime dependency on:

- `Task`;
- `PlanStep`;
- `ExecutionPlan`;
- `AgentRegistry`;
- `TaskRouter`;
- `ExecutionPlanner`.

### V2

After core hardening:

- define a project-planning capability;
- register all agents consistently;
- route PlanningAgent through the same runtime as other agents;
- introduce an executor before claiming multi-agent orchestration.

### Naming Protection

Documentation and code should consistently use:

- **PlanningAgent** for project discovery and artifact generation;
- **ExecutionPlanner** for runtime agent-step planning.

Avoid generic references such as “the planner” where the meaning is ambiguous.

## Provider Integration

PlanningAgent should depend conceptually on `BaseProvider`, not directly on `OllamaProvider`.

Benefits:

- `MockProvider` can test AI-assisted branches;
- provider unavailability can be simulated;
- deterministic mode remains the default;
- local Ollama remains an implementation choice rather than agent logic.

Provider output must be validated against structured input before writing. At minimum:

- no new decisions;
- no removed constraints;
- no invented requirements;
- no changed IDs;
- no changed task dependencies.

## Worker Integration

PlanningAgent uses only file operations.

The output path should resolve under an explicitly selected root. Before implementation, `FileWorker` should enforce real containment when `base_path` is supplied.

The write should be treated as one logical planning package:

- generate all content in memory;
- validate cross-references;
- preview planned paths;
- write;
- report partial failure accurately.

True atomic multi-file transactions are not currently available. V1 should acknowledge this and avoid claiming atomicity.

## Future Bootstrap Integration

`bootstrap` should consume the planning package through a dedicated reader/validator, not by scraping arbitrary prose.

Bootstrap eligibility should require:

- supported `planning_schema`;
- accepted required decisions;
- no unresolved blocking questions;
- valid task and requirement references;
- no circular dependencies;
- explicit user confirmation;
- supported stack choices.

Bootstrap should read:

- `REQUIREMENTS.md` for scope and constraints;
- accepted decision records for technology choices;
- `ARCHITECTURE.md` for component boundaries;
- `TASK.md` for sequencing.

Bootstrap must not assume every task is executable by an agent. Human tasks, research tasks, and unsupported implementation work remain human-owned.

## Compatibility Strategy

PlanningAgent should be additive:

- no change to current command names;
- no change to existing output paths;
- no automatic invocation from `all`;
- no requirement that existing repositories adopt `project-plan/`;
- no automatic modification of README, Docker, Kubernetes, or CI files;
- no provider requirement;
- no core orchestration requirement.

PlanningAgent should not be added to `all` in V1. Planning a project is an interactive, intent-changing workflow and does not belong in a bulk generation command.

# Section 11 — Risks and Mitigations

## Overengineering Risk

### Risk

PlanningAgent could expand into:

- a full project-management system;
- a requirements database;
- a graph engine;
- a workflow scheduler;
- a plugin platform;
- an autonomous software factory.

### Mitigation

- use four artifact types only;
- use Markdown and stable IDs;
- keep statuses and priorities small;
- ask a bounded question set;
- exclude calendars, estimates, sprints, comments, notifications, and dashboards;
- require a concrete consumer before adding metadata.

## Memory Risk

### Risk

Persistent files can become stale, contradictory, or treated as infallible.

### Mitigation

- define source-of-truth precedence;
- record status and update date;
- use superseding decision records;
- validate links and conflicts;
- separate detected facts from decisions;
- keep open questions visible;
- never hide changes in model memory.

## AI Hallucination Risk

### Risk

Ollama may invent requirements, components, constraints, or implementation claims.

### Mitigation

- deterministic structured data is authoritative;
- AI is optional;
- use AI for prose only;
- show a confirmation summary;
- preserve unknowns;
- validate that IDs and facts did not change;
- test AI paths with `MockProvider`.

## Complexity Risk

### Risk

Interactive sessions, parsing, updates, and cross-references can create more complexity than the current codebase can support.

### Mitigation

- V1 creates new plans only;
- defer resume/update parsing to V2;
- use a fixed schema version;
- avoid integrating the unused core in V1;
- keep the first question catalog static;
- avoid generic workflow engines.

## Maintenance Risk

### Risk

Markdown templates and question sets may diverge or duplicate logic.

### Mitigation

- centralize planning models;
- centralize document rendering in one planning generator;
- give each field one owner;
- add golden-output tests;
- validate cross-document references;
- keep provider prompts outside document structure.

## File Safety Risk

### Risk

PlanningAgent may overwrite valuable human-edited project memory or write outside the intended directory.

### Mitigation

- no overwrite by default;
- harden path containment first;
- show target paths before writes;
- avoid broad overwrite for decision records;
- create new superseding records;
- report partial failures truthfully;
- never use shell commands for file generation.

## Scope Authority Risk

### Risk

The agent may appear to make product decisions on behalf of the user.

### Mitigation

- every consequential choice requires confirmation;
- suggestions remain labeled suggestions;
- unresolved choices remain open questions;
- generated documents identify sources;
- accepted decision status belongs to the user.

## Bootstrap Coupling Risk

### Risk

Designing PlanningAgent around an imagined bootstrap implementation could create speculative fields and premature abstractions.

### Mitigation

- store only information useful to humans now;
- use stable IDs and a schema version for future parsing;
- defer executable action schemas until bootstrap is designed;
- do not encode shell commands into tasks;
- keep task objectives separate from agent execution steps.

## Existing Architecture Risk

### Risk

PlanningAgent could be used to justify prematurely activating the incomplete router/planner/registry stack.

### Mitigation

- direct CLI dispatch in V1;
- no `ExecutionPlan` dependency;
- core integration only after an executor, tests, and consistent registration exist;
- document the distinction between project planning and runtime planning.

# Section 12 — Implementation Roadmap

The roadmap is intentionally gated. Phase 1 is prerequisite hardening, not PlanningAgent feature code.

## Phase 1 — Baseline Reliability Gate

Complete before PlanningAgent writes persistent memory:

1. add CLI tests for current command parsing and exit codes;
2. fix the broken `all` command and truthful error propagation;
3. fix agent result semantics for created, skipped, dry-run, and failed files;
4. add FileWorker tests for overwrite and dry-run behavior;
5. enforce real `base_path` containment or stop describing it as a restriction;
6. add provider lifecycle and fallback tests;
7. establish a clean test environment in the repository;
8. document the actual global-option placement.

Exit criteria:

- existing command tests pass;
- failed writes cannot produce a successful result;
- dry-run performs no writes;
- path containment is verified;
- PlanningAgent can rely on safe, truthful file output.

## Phase 2 — Minimal PlanningAgent V1

Build only the initial creation workflow:

1. define planning-specific structured models and schema version;
2. define a bounded deterministic question catalog;
3. define answer normalization and open-question handling;
4. create a dedicated planning document generator;
5. create PlanningAgent using BaseAgent and FileWorker;
6. add direct `plan` CLI dispatch;
7. generate the four artifact groups;
8. add confirmation before accepted decisions and writes;
9. support dry-run and default overwrite protection;
10. add unit, generator, CLI, and golden-output tests.

Exit criteria:

- works without Ollama;
- creates internally consistent planning files;
- never executes shell commands;
- does not modify existing commands;
- does not silently accept unknown choices;
- all cross-references validate.

## Phase 3 — Controlled PlanningAgent V2

Add plan evolution only after V1 is stable:

1. parse existing planning packages;
2. validate schema and references;
3. add resume/update workflows;
4. implement decision supersession;
5. preserve human-edited content where ownership permits;
6. add optional RepoAnalyzer context;
7. add drift reporting;
8. inject optional `BaseProvider`;
9. use MockProvider in tests;
10. add conflict and migration tests.

Exit criteria:

- accepted decision history is preserved;
- updates change only affected artifacts;
- detected repository facts never silently override user decisions;
- provider failure leaves a complete deterministic plan.

## Phase 4 — Future Bootstrap and Core Integration

Proceed only after the current core orchestration is made real:

1. design a plan reader/validator contract;
2. define bootstrap eligibility rules;
3. distinguish human tasks from executable agent tasks;
4. add a tested execution engine for `ExecutionPlan`;
5. register all agents consistently;
6. route all commands consistently or retain direct dispatch consistently;
7. translate approved planning inputs into deterministic agent tasks;
8. require execution preview and confirmation;
9. update task status only from verified results;
10. keep deployment and destructive actions outside automatic bootstrap.

Exit criteria:

- no special-case orchestration for PlanningAgent;
- unresolved decisions block dependent execution;
- bootstrap consumes stable plan data without inventing choices;
- failures are visible and recoverable;
- existing agents remain independently usable.

# Section 13 — Final Recommendation

## 1. Should PlanningAgent Be Built Now?

**The design should be approved now, but implementation should not begin before the Phase 1 reliability gate.**

PlanningAgent is a coherent next feature because it:

- matches the CLI-first product;
- produces reviewable files;
- uses local optional AI appropriately;
- creates a foundation for future bootstrap;
- adds depth rather than unrelated breadth.

However, persistent project memory depends on truthful writes, safe paths, reliable dry-run behavior, and tests. The current repository does not yet meet that baseline.

After Phase 1, a tightly scoped PlanningAgent V1 is reasonable. It should not wait for every Docker/Kubernetes/CI template to become production-grade, but it should wait for shared CLI, result, worker, and provider foundations to be trustworthy.

## 2. What Should Be Completed First?

Before PlanningAgent implementation:

1. CLI and worker tests;
2. truthful agent result handling;
3. `all` command repair;
4. file path containment;
5. dry-run and overwrite correctness;
6. provider injection/lifecycle basics if Ollama will be used;
7. a clear distinction between the active direct-dispatch architecture and the future core architecture.

## 3. What Should Be Postponed?

Postpone:

- plan update/resume;
- repository drift analysis;
- Ollama-generated question selection;
- router/registry/planner integration;
- automatic task-status updates;
- bootstrap;
- code generation from tasks;
- cloud-specific architecture generation;
- multiple planning schemas;
- import/export formats beyond Markdown;
- collaboration and project-management features.

## 4. What Should Never Be Added?

PlanningAgent should never become:

- an autonomous code-writing loop hidden behind `plan`;
- a shell-executing planning command;
- an agent swarm coordinator;
- a hidden vector-memory system;
- a source of unconfirmed architecture decisions;
- a secrets store;
- a cloud dashboard requirement;
- a replacement for human product ownership;
- an automatic production deployment path;
- a mechanism that marks work complete without verified evidence.

## Final Position

PlanningAgent is the right conceptual evolution for Sohail-Agent-CLI only if it remains small, explicit, local, and file-based.

The recommended V1 is:

> A deterministic interactive planning agent that asks bounded questions, records confirmed decisions, generates four kinds of Markdown planning artifacts, uses safe file writes, and stops before implementation.

That version strengthens the project’s identity without pretending the current repository is already an autonomous multi-agent platform.


---

# Engineering Decision Engine Architecture

## Document Purpose

This document defines the proposed next-generation Planning system for Sohail-Agent-CLI: the Engineering Decision Engine, or EDE. It is an architecture specification, not an implementation plan. It describes the conceptual model, system boundaries, validation responsibilities, renderer abstraction, extensibility model, and downstream contracts required for another engineer to implement the subsystem without inventing new architecture.

The Engineering Decision Engine replaces assumption-driven planning with explicit engineering decision capture. It becomes the authoritative decision source for every downstream subsystem in Sohail-Agent-CLI.

## 1. Vision

The Engineering Decision Engine exists to make software generation predictable, inspectable, and grounded in user-approved engineering intent.

The current planning workflow relies on AI interpretation and interactive questions to infer what a project needs. That approach is useful for exploration, but it creates architectural risk when downstream agents must guess critical decisions such as backend framework, database, deployment platform, authentication model, testing strategy, compliance needs, or observability requirements. These are not cosmetic choices. They shape generated code, project layout, dependencies, infrastructure, security posture, documentation, and future maintenance cost.

AI guessing project requirements creates several recurring problems:

- It may infer requirements the user never approved.
- It may choose technologies that conflict with the user's organization, budget, or deployment environment.
- It may produce inconsistent outputs across agents because each subsystem interprets the planning package differently.
- It may hide important decisions inside prose instead of making them structured and verifiable.
- It may force downstream agents to compensate for missing context with more AI inference.
- It makes generated software harder to audit because there is no single decision record explaining why the project was shaped a certain way.

The Engineering Decision Engine addresses these problems by capturing explicit engineering decisions before any AI generation happens. The user, organization profile, template defaults, capability packs, validation rules, and optional AI recommendations all contribute to a structured decision record. Final authority remains with the user or an approved policy source, never with autonomous AI inference.

Explicit engineering decisions improve software generation because every downstream subsystem receives the same normalized source of truth. BootstrapAgent can scaffold the right project shape. StackAgent can select compatible technology skeletons. SpecificationAgent can translate product intent into precise requirements without guessing the platform. BlueprintAgent can design implementation architecture from already-approved decisions. Future agents can implement, test, deploy, and review using the same canonical selection model.

EDE becomes the single source of truth for project engineering intent. The planning package remains the portable artifact, but its core content is no longer just markdown prose. It is backed by a strongly validated PlanningSelections record that documents what was selected, why it was selected, where it came from, and whether it is required, optional, recommended, overridden, or unresolved.

## 2. High-Level Architecture

The Engineering Decision Engine sits between the user and all generation subsystems. It turns project intent into validated engineering decisions before any downstream agent runs.

Conceptual flow:

User

↓

Engineering Decision Engine

↓

PlanningSelections

↓

Planning Package

↓

BootstrapAgent

↓

StackAgent

↓

SpecificationAgent

↓

BlueprintAgent

↓

Future ImplementationAgent

### Stage Responsibilities

User:

- Provides project goal, constraints, preferences, organization context, and overrides.
- Accepts or rejects template defaults, capability packs, profile standards, and AI recommendations.
- Owns final approval of all engineering decisions.

Engineering Decision Engine:

- Orchestrates decision capture.
- Applies project templates, organization profiles, and capability packs.
- Presents questions through renderer-neutral interfaces.
- Records explicit user choices.
- Requests optional AI recommendations where useful.
- Validates completeness, compatibility, and policy compliance.
- Produces the canonical PlanningSelections record.
- Produces a planning package consumable by existing and future agents.

PlanningSelections:

- Stores normalized, typed engineering decisions.
- Separates user-selected values from defaults, recommendations, and inferred metadata.
- Records provenance for each decision.
- Captures unresolved decisions and validation warnings.
- Serves as the structured contract between planning and generation.

Planning Package:

- Persists the planning outcome in a portable project-plan directory.
- Contains human-readable markdown documents for review.
- Contains or represents structured decision data that downstream systems can load deterministically.
- Preserves compatibility with existing PlanningAgent output expectations.

BootstrapAgent:

- Consumes project identity, architecture style, folder conventions, documentation expectations, and baseline setup decisions.
- Generates project scaffold using explicit selections rather than deriving structure from prose.

StackAgent:

- Consumes frontend, backend, database, cloud, containerization, CI/CD, testing, and dependency selections.
- Generates technology-specific skeletons only for approved technologies.
- Avoids choosing default stacks independently.

SpecificationAgent:

- Consumes project decisions and planning documents.
- Produces product, feature, data, API, and non-functional specifications aligned with selected engineering constraints.
- Does not need to infer architecture, security, deployment, or compliance assumptions.

BlueprintAgent:

- Consumes planning and specification outputs.
- Produces system design, backend architecture, frontend architecture, database design, API flow, implementation plan, folder structure, and dependencies from explicit decisions.
- Treats PlanningSelections as architectural boundaries.

Future ImplementationAgent:

- Consumes the same decision source to generate application code.
- Uses approved architecture, stack, dependencies, testing strategy, and security posture.
- Reports conflicts when requested implementation work exceeds approved decisions.

### Architectural Boundary

EDE is the decision authority. Downstream agents are generation executors. They may validate that required decisions exist, but they must not invent missing decisions. If a downstream subsystem lacks required context, it should fail with a clear planning error and request an EDE update.

## 3. Core Design Principles

User decisions over AI assumptions:

- User selections and approved policy sources are authoritative.
- AI output is advisory until explicitly accepted.
- Generated artifacts must be traceable to approved decisions.

AI recommends but never decides:

- AI may propose choices, explain tradeoffs, warn about risk, or review completeness.
- AI must not silently add, remove, or override selections.
- AI recommendations must be represented separately from final decisions.

Single source of truth:

- PlanningSelections is the canonical decision model.
- Markdown documents are renderings of decisions, not independent truth.
- Downstream agents consume structured decisions where available and use markdown for human context.

Strong typing:

- Each decision has a defined value shape, allowed values, cardinality, provenance, and validation rules.
- Free-form text is allowed only where the domain requires custom expression.
- Ambiguous string blobs should not represent structured engineering choices.

Extensibility:

- New sections, technologies, templates, profiles, rules, and capability packs can be added without redesigning the engine.
- Extension points must be explicit and versioned.
- Core engine behavior should not depend on hard-coded knowledge of every future technology.

Plugin architecture:

- External plugins can register domain-specific questions, templates, options, capability packs, validation rules, and profiles.
- Plugins extend decision vocabulary without modifying the core repository.
- Plugin contributions must be namespaced and validated.

Backward compatibility:

- EDE must preserve the existing project-plan contract expected by BootstrapAgent, StackAgent, SpecificationAgent, and BlueprintAgent until those agents are upgraded.
- Existing markdown files such as TASK.md, REQUIREMENTS.md, ARCHITECTURE.md, and decisions must remain available.
- New structured artifacts should enhance, not immediately replace, existing planning package content.

Deterministic outputs:

- Given the same inputs, profiles, templates, packs, overrides, and accepted recommendations, EDE should produce the same PlanningSelections and planning package.
- AI recommendations are captured as inputs with provenance, not hidden nondeterministic mutations.

Validation before generation:

- PlanningSelections must be validated before downstream agents run.
- Missing required selections, conflicts, deprecated technologies, and unsupported combinations must be reported early.
- Generation should proceed only when the decision record satisfies the minimum requirements for the selected workflow.

Explainability:

- Decisions should record why they exist and where they came from.
- Users should be able to inspect defaults, overrides, recommendations, and validation warnings.
- Downstream artifacts should be auditable against the decision record.

Progressive disclosure:

- Simple projects should not require enterprise-level decision volume.
- Templates, profiles, and capability packs should determine which questions are required.
- Advanced decisions should be available without overwhelming basic workflows.

## 4. Engineering Decision Model

PlanningSelections is the complete decision record produced by EDE. It represents the project as structured engineering intent.

Each decision section should support:

- Selected values.
- Default values.
- User overrides.
- Recommendation references.
- Provenance.
- Validation status.
- Confidence or certainty where applicable.
- Human-readable rationale.
- Downstream relevance.

Each individual decision should identify whether it is required, optional, recommended, blocked, deprecated, unsupported, or unresolved.

### Project

The Project section captures identity and product intent.

It should include:

- Project name.
- Short description.
- Primary goal.
- Target users.
- Domain.
- Product type.
- Project lifecycle stage.
- Expected scale.
- Repository target.
- Output directory preferences.
- Ownership metadata.

This section exists because every downstream artifact needs a stable project identity and goal. It prevents agents from inventing names, domains, user groups, or scale assumptions.

### Architecture

The Architecture section captures the top-level application style.

It should include:

- Architecture pattern, such as monolith, modular monolith, microservices, serverless, event-driven, plugin-based, or hybrid.
- Service boundaries.
- API style.
- Frontend/backend separation.
- Internal module boundaries.
- Integration strategy.
- Synchronous and asynchronous communication choices.
- Scalability expectations.

This section exists because architecture style affects folder structure, code organization, deployment topology, testing strategy, operational complexity, and implementation sequencing.

### Frontend

The Frontend section captures user interface technology and experience decisions.

It should include:

- Whether a frontend is required.
- Frontend framework.
- Rendering model.
- Styling approach.
- Component system.
- State management.
- Routing.
- Forms strategy.
- Accessibility expectations.
- Internationalization needs.
- Mobile or responsive requirements.

This section exists because generated frontend code depends on approved frameworks and UX constraints. It prevents downstream agents from assuming React, Next.js, Vue, or no frontend without permission.

### Backend

The Backend section captures server-side application decisions.

It should include:

- Whether a backend is required.
- Backend language.
- Framework.
- API style.
- Module organization.
- Service layer pattern.
- Background job strategy.
- Configuration strategy.
- Error handling approach.
- Dependency injection preferences.
- Runtime environment.

This section exists because backend generation must align with selected language, framework, service boundaries, and runtime expectations.

### Database

The Database section captures persistence decisions.

It should include:

- Whether persistent storage is required.
- Database type.
- Specific database technology.
- ORM or query layer.
- Migration strategy.
- Multi-tenancy strategy.
- Backup expectations.
- Data retention expectations.
- Local development database strategy.
- Production database strategy.

This section exists because data modeling, generated dependencies, environment variables, infrastructure, and tests all depend on persistence choices.

### Caching

The Caching section captures performance and state acceleration decisions.

It should include:

- Whether caching is required.
- Cache technology.
- Cache scope.
- Cache invalidation strategy.
- Time-to-live expectations.
- Session cache needs.
- API response caching needs.

This section exists because caching introduces infrastructure dependencies and consistency tradeoffs. It should be explicit, especially when Redis, CDN caching, or application-level caching is introduced.

### Queues

The Queues section captures asynchronous processing decisions.

It should include:

- Whether queues are required.
- Queue technology.
- Job types.
- Retry strategy.
- Dead-letter handling.
- Scheduling needs.
- Worker deployment model.

This section exists because queue selection affects backend architecture, infrastructure, deployment, observability, and failure handling.

### Authentication

The Authentication section captures identity verification decisions.

It should include:

- Whether authentication is required.
- Authentication model.
- Identity provider.
- Session or token strategy.
- Social login requirements.
- Password policy.
- Multi-factor authentication requirements.
- Machine-to-machine authentication needs.

This section exists because authentication affects data model, API security, frontend flows, backend middleware, secrets, and compliance posture.

### Authorization

The Authorization section captures access control decisions.

It should include:

- Whether authorization is required.
- Role-based, attribute-based, policy-based, or custom authorization model.
- Roles.
- Permissions.
- Resource ownership rules.
- Administrative access rules.
- Tenant isolation rules.

This section exists because authorization is not the same as authentication. Downstream agents need explicit permission models to generate secure APIs, UI gates, tests, and documentation.

### Storage

The Storage section captures file and object storage decisions.

It should include:

- Whether file storage is required.
- Storage provider.
- Local development storage.
- Upload constraints.
- File type restrictions.
- Public versus private access.
- Retention policy.
- Virus scanning expectations.

This section exists because storage choices affect infrastructure, backend services, security controls, and user workflows.

### Search

The Search section captures discovery and indexing decisions.

It should include:

- Whether search is required.
- Search technology.
- Indexed entities.
- Full-text needs.
- Faceting needs.
- Ranking needs.
- Reindexing strategy.
- Search latency expectations.

This section exists because search may require specialized infrastructure, data synchronization, and API design.

### Notifications

The Notifications section captures messaging decisions.

It should include:

- Whether notifications are required.
- Channels such as email, SMS, push, in-app, webhook, or chat.
- Provider preferences.
- Template management.
- Delivery tracking.
- Retry behavior.
- User preferences.
- Compliance requirements for communications.

This section exists because notifications affect user flows, background jobs, third-party integrations, secrets, and audit requirements.

### Monitoring

The Monitoring section captures operational visibility decisions.

It should include:

- Metrics requirements.
- Uptime checks.
- Health check endpoints.
- Alerting provider.
- Service-level objectives.
- Dashboard expectations.
- Incident response hooks.

This section exists because production-ready systems need observability decisions before deployment artifacts are generated.

### Logging

The Logging section captures application and infrastructure logging decisions.

It should include:

- Logging format.
- Log levels.
- Structured logging requirements.
- Correlation ID strategy.
- Log retention.
- Sensitive data redaction.
- Centralized log provider.

This section exists because logging affects generated middleware, runtime configuration, debugging, compliance, and observability.

### Cloud

The Cloud section captures hosting and managed service decisions.

It should include:

- Cloud provider.
- Region preferences.
- Environment strategy.
- Managed services.
- Networking expectations.
- Secrets management.
- Infrastructure ownership.
- Local versus cloud parity expectations.

This section exists because cloud choices determine deployment topology, infrastructure dependencies, environment variables, and cost profile.

### Containerization

The Containerization section captures packaging and runtime isolation decisions.

It should include:

- Whether containers are required.
- Dockerfile strategy.
- Compose strategy.
- Base image preferences.
- Multi-stage build expectations.
- Runtime user expectations.
- Image registry.
- Local development container strategy.

This section exists because containerization affects project files, build pipelines, security, deployment, and developer experience.

### CI/CD

The CI/CD section captures automation decisions.

It should include:

- CI provider.
- Build workflow.
- Test workflow.
- Lint workflow.
- Deployment workflow.
- Release strategy.
- Branch strategy.
- Artifact publishing.
- Required approvals.

This section exists because automation should match organization standards and deployment choices rather than being guessed by a generator.

### Testing

The Testing section captures quality strategy.

It should include:

- Unit testing framework.
- Integration testing approach.
- End-to-end testing approach.
- Contract testing needs.
- Performance testing needs.
- Security testing needs.
- Test data strategy.
- Coverage expectations.

This section exists because generated code should include the right test shape from the start.

### Security

The Security section captures cross-cutting security decisions.

It should include:

- Threat model level.
- Secrets strategy.
- Dependency scanning.
- Static analysis.
- Runtime protections.
- Rate limiting.
- CORS strategy.
- Input validation expectations.
- Audit logging.
- Encryption requirements.

This section exists because security cannot be reliably added after generation. It must influence architecture, dependencies, configuration, and tests.

### Documentation

The Documentation section captures documentation expectations.

It should include:

- README expectations.
- API documentation.
- Architecture decision records.
- Developer guide.
- Operations guide.
- User-facing documentation.
- Changelog strategy.
- Documentation format.

This section exists because generated projects should be understandable and maintainable from the first scaffold.

### Compliance

The Compliance section captures regulatory and policy constraints.

It should include:

- Applicable standards.
- Data classification.
- Audit requirements.
- Retention rules.
- Privacy requirements.
- Consent requirements.
- Regional constraints.
- Review requirements.

This section exists because compliance affects data model, logging, storage, security, deployment, and operational processes.

### Performance Goals

The Performance Goals section captures measurable non-functional expectations.

It should include:

- Expected users.
- Expected requests per second.
- Latency targets.
- Availability targets.
- Data volume expectations.
- Build time expectations.
- Startup time expectations.
- Resource constraints.

This section exists because performance goals guide architecture selection, caching, database design, deployment topology, and test strategy.

### Budget Constraints

The Budget Constraints section captures cost boundaries.

It should include:

- Monthly budget range.
- Preferred free-tier usage.
- Managed service limits.
- Cloud provider cost sensitivity.
- Operational complexity tolerance.
- Team size.
- Maintenance capacity.

This section exists because technically valid architectures may be inappropriate for a user's budget or team capacity.

### Custom Requirements

The Custom Requirements section captures arbitrary project-specific engineering needs.

It should include:

- Requirement title.
- Requirement description.
- Category.
- Priority.
- Acceptance criteria.
- Affected subsystems.
- Validation needs.
- Downstream consumption notes.

This section exists because no fixed schema can anticipate every product or engineering requirement. It gives users a formal way to add unique constraints without hiding them in prose.

### AI Capabilities

The AI Capabilities section captures explicit AI feature decisions for the generated project.

It should include:

- Whether the application includes AI-powered features.
- AI use cases.
- Provider preferences.
- Model constraints.
- Data privacy constraints.
- Prompt logging policy.
- Human review requirements.
- Fallback behavior.
- Cost limits.

This section exists because AI features introduce product behavior, privacy, cost, evaluation, and operational concerns. They must be planned explicitly.

### Recommendations

The Recommendations section captures advisory suggestions that have not necessarily been accepted.

It should include:

- Recommendation title.
- Source.
- Rationale.
- Impact.
- Confidence.
- Related decisions.
- User disposition.
- Accepted or rejected timestamp where applicable.

This section exists to keep advisory input transparent without confusing it with approved engineering decisions.

## 5. Question Engine

The Question Engine is the renderer-neutral mechanism for collecting decisions. It should define questions as structured decision prompts, not CLI-specific interactions.

Each question should include:

- Stable identifier.
- Section ownership.
- Prompt text.
- Help text.
- Question type.
- Required status.
- Default value.
- Allowed options where applicable.
- Validation rules.
- Dependency conditions.
- Visibility conditions.
- Provenance tracking.
- Recommendation hooks.
- Renderer hints.

The question representation must be independent of command-line parsing, terminal formatting, or interactive input mechanics. Renderers decide how to display questions, but the engine decides what must be asked, when it must be asked, and how answers are validated.

### Text

Text questions collect short or long free-form input.

They are appropriate for project names, descriptions, rationales, custom requirements, business context, and notes. Text questions should support length constraints, required patterns, and multiline behavior.

### Single Choice

Single choice questions collect exactly one option from a known set.

They are appropriate for framework selection, cloud provider, architecture style, database technology, CI provider, and authentication model. Options should carry labels, descriptions, compatibility metadata, deprecation status, and plugin namespace where applicable.

### Multiple Choice

Multiple choice questions collect zero or more options from a known set.

They are appropriate for notification channels, testing types, documentation outputs, capability packs, compliance standards, and monitoring features. Multiple choice questions should define minimum and maximum selection counts where needed.

### Boolean

Boolean questions collect yes or no decisions.

They are appropriate for enabling optional subsystems such as authentication, caching, queues, search, Docker, CI/CD, or AI features. Boolean questions often act as gates for additional follow-up questions.

### Number

Number questions collect integer or decimal values.

They are appropriate for budget, expected users, latency targets, retention periods, coverage thresholds, replicas, and rate limits. Number questions should support ranges, units, and precision rules.

### Path

Path questions collect file system or repository paths.

They are appropriate for output directories, monorepo package locations, existing repository paths, documentation locations, and configuration file locations. Path questions should support existence requirements, relative path policy, and write-safety constraints.

### Secret

Secret questions collect sensitive values.

They are appropriate only when a planning flow truly needs a secret reference. EDE should prefer secret names, provider references, or environment variable names over raw secret values. Secret answers must not be written into human-readable planning documents.

### Tags

Tags questions collect a set of free-form labels.

They are appropriate for product domains, feature categories, deployment environments, risk areas, team labels, and custom grouping. Tags should support normalization, duplicate handling, and optional allowed prefixes.

## 6. Project Templates

Project templates provide opinionated default engineering decisions for common application categories. They reduce planning friction by starting from a coherent baseline instead of asking every question from scratch.

Templates should provide:

- Default project type.
- Recommended architecture style.
- Common frontend and backend defaults.
- Common persistence choices.
- Typical authentication and authorization needs.
- Expected testing and documentation levels.
- Common capability packs.
- Common validation rules.
- Template-specific questions.
- Rationale for defaults.

Templates must never lock the user into defaults. Users can accept, override, remove, or extend template selections. Overrides become explicit decisions with provenance showing the original template default and the user-approved replacement.

### Task Management

The Task Management template should default to user accounts, projects or workspaces, task entities, status workflows, filtering, notifications, and common CRUD APIs. It may recommend authentication, authorization, database persistence, frontend forms, and basic audit logging.

### CRM

The CRM template should default to contacts, accounts, interactions, activity history, role-based access, import/export, search, reporting, and email integration. It may recommend analytics, notifications, and stricter data retention settings.

### ERP

The ERP template should default to modular architecture, strong authorization, audit trails, reporting, workflow approvals, integrations, and robust database modeling. It may recommend modular monolith or microservices depending on scale.

### Healthcare

The Healthcare template should default to strong privacy, audit logging, data retention, access controls, secure storage, compliance review, and careful AI usage policies. It may recommend conservative technology choices and explicit compliance selection.

### Education

The Education template should default to users, courses, assignments, content management, progress tracking, notifications, and accessibility requirements. It may recommend role models for students, instructors, and administrators.

### Inventory

The Inventory template should default to products, stock movements, warehouses, suppliers, reporting, barcode or SKU support, and audit trails. It may recommend database constraints, background jobs, and import/export capabilities.

### Blog

The Blog template should default to content entities, authoring workflow, public pages, SEO, media storage, and optional comments. It may recommend static generation, CMS-style administration, and search.

### AI SaaS

The AI SaaS template should default to user accounts, billing readiness, AI provider configuration, usage tracking, prompt privacy, rate limiting, observability, and cost controls. It may recommend AI capability packs and security packs.

### DevOps Platform

The DevOps Platform template should default to repository integrations, job execution, audit logging, secrets references, role-based access, observability, and deployment workflows. It may recommend queues, containers, monitoring, and policy controls.

### Blank

The Blank template should provide minimal defaults. It is appropriate when users want full control or when no domain template fits. It should still collect required project identity and core architecture decisions.

## 7. Dependency Rules

Dependency rules ensure that selections form a coherent engineering system.

Rules should identify:

- Required dependencies.
- Recommended dependencies.
- Mutually exclusive selections.
- Unsupported combinations.
- Deprecated selections.
- Provider-specific constraints.
- Capability prerequisites.
- Security or compliance implications.

Dependency validation should be explainable. A rule should report what triggered it, why it matters, what decisions are affected, and how the user can resolve the issue.

Examples:

- Next.js requires React.
- Redis Queue requires Redis.
- EKS requires AWS.
- Microservices recommend API Gateway.
- Serverless architecture may conflict with long-running background workers unless a compatible queue or worker service is selected.
- OAuth authentication requires an identity provider.
- Object storage with private file access requires signed URL or proxy strategy.
- OpenTelemetry requires compatible monitoring or tracing export configuration.
- PostgreSQL with ORM migrations requires a migration strategy.
- Healthcare compliance requires audit logging and data retention decisions.

### Dependency Resolution Strategy

The engine should resolve dependencies in phases:

- Collect initial selections from template, profile, packs, user answers, and accepted recommendations.
- Normalize equivalent choices into canonical decision values.
- Apply required dependency rules.
- Apply mutually exclusive and unsupported combination rules.
- Apply recommendation rules.
- Present required fixes before optional improvements.
- Record accepted automatic additions only when the user explicitly approves them.
- Revalidate after each change until the decision set is complete or intentionally blocked.

Dependency resolution should not silently mutate final selections. If a dependency must be added, the engine should present the requirement and ask for confirmation or an alternative.

## 8. AI Recommendation Engine

The AI Recommendation Engine provides advisory intelligence on top of explicit decision capture. It helps users make better engineering decisions without becoming the decision-maker.

AI may suggest:

- Docker.
- Swagger or OpenAPI documentation.
- Health checks.
- Redis.
- Monitoring.
- Caching.
- Rate limiting.
- Structured logging.
- OpenTelemetry.
- API Gateway.
- Background queues.
- Security scanning.
- Accessibility testing.
- Backup strategy.

Recommendations should include:

- Recommendation title.
- Rationale.
- Benefits.
- Tradeoffs.
- Cost or complexity impact.
- Related decisions.
- Confidence.
- Whether the recommendation is optional, recommended, or strongly recommended.
- User action: accept, reject, defer, or request explanation.

AI must never automatically modify user selections. Accepted recommendations become normal decisions with provenance indicating that they originated as AI recommendations and were approved by the user. Rejected recommendations remain recorded when useful for auditability, but they must not influence downstream generation.

AI recommendations should be deterministic at the decision record level. The recommendation text may vary, but accepted selections must be captured explicitly so downstream agents do not depend on re-running the same AI prompt.

## 9. Custom Engineering Requirements

Custom Engineering Requirements allow users to add arbitrary engineering requirements beyond the fixed PlanningSelections schema.

Examples:

- Use AI for document summarization.
- Generate PDF reports.
- Offline mode.
- AI code inspection.
- Support CSV imports.
- Provide admin impersonation.
- Integrate with Slack.
- Support tenant-level branding.
- Keep a full audit trail of financial changes.

Each custom requirement should include:

- Title.
- Description.
- Priority.
- Category.
- Affected sections.
- Acceptance criteria.
- Constraints.
- Open questions.
- Downstream consumers.
- Validation status.

Custom requirements become part of PlanningSelections as first-class decision records. They are not loose notes. They should be addressable, traceable, and available to downstream agents.

Downstream agents consume custom requirements as follows:

- BootstrapAgent may create folders, placeholders, documentation sections, or configuration surfaces when a custom requirement affects project shape.
- StackAgent may select or warn about missing technologies required by a custom requirement.
- SpecificationAgent should translate custom requirements into product, feature, API, data, and non-functional specifications.
- BlueprintAgent should include custom requirements in system design, implementation plan, dependencies, and folder structure.
- Future ImplementationAgent should treat custom requirements as implementation obligations or explicit constraints.
- Future TestingAgent should derive test obligations from acceptance criteria.
- Future ReviewAgent should check generated work against custom requirements.

Custom requirements should support validation hooks. For example, "Generate PDF reports" may require a document generation library, storage decision, or background job strategy. "Offline mode" may require local storage, synchronization, conflict resolution, and frontend architecture decisions.

## 10. Capability Packs

Capability packs are reusable bundles of engineering decisions, questions, dependencies, and validation rules that add a cross-cutting capability to a project.

Capability packs differ from templates:

- Templates describe a project type.
- Capability packs describe reusable technical capability.
- A project usually has one primary template.
- A project may use many capability packs.
- Templates provide broad defaults.
- Capability packs add focused behavior and supporting decisions.

Capability packs should provide:

- Capability description.
- Included decisions.
- Additional questions.
- Required dependencies.
- Recommended dependencies.
- Validation rules.
- Downstream generation notes.
- Documentation obligations.
- Testing obligations.

### AI Pack

The AI Pack should add AI provider selection, model constraints, prompt privacy, cost controls, usage tracking, fallback behavior, and human review policies.

### Observability Pack

The Observability Pack should add structured logging, metrics, tracing, health checks, dashboards, alerting, and correlation IDs.

### Security Pack

The Security Pack should add rate limiting, dependency scanning, static analysis, secrets handling, audit logging, secure headers, and threat model expectations.

### Analytics Pack

The Analytics Pack should add event tracking, reporting, dashboards, retention policy, privacy constraints, and export requirements.

### Payments Pack

The Payments Pack should add payment provider selection, webhook handling, billing models, audit logging, idempotency, compliance notes, and test mode requirements.

### Search Pack

The Search Pack should add search provider, indexed entities, reindexing, ranking, filters, and search API expectations.

### Notifications Pack

The Notifications Pack should add channel selection, provider choices, templates, delivery tracking, retries, and user preferences.

### Developer Experience Pack

The Developer Experience Pack should add linting, formatting, pre-commit hooks, local development scripts, seed data, documentation, and onboarding workflows.

## 11. Organization Profiles

Organization profiles represent reusable standards for a team, company, institution, or regulated environment.

Profiles should include:

- Approved technologies.
- Deprecated or forbidden technologies.
- Preferred cloud provider.
- Preferred CI/CD provider.
- Security baseline.
- Documentation standards.
- Testing standards.
- Compliance requirements.
- Observability standards.
- Naming conventions.
- Deployment policies.
- Cost preferences.

Example profiles:

- Startup.
- Enterprise.
- Healthcare.
- Government.
- Education.
- FinTech.

### Startup

The Startup profile should favor fast delivery, low operational overhead, managed services, simple deployment, basic observability, and cost awareness.

### Enterprise

The Enterprise profile should favor governance, auditability, strong CI/CD controls, role-based access, standardized observability, documentation, and compliance readiness.

### Healthcare

The Healthcare profile should favor privacy, audit logging, strict access control, retention policies, cautious AI usage, and compliance review.

### Government

The Government profile should favor security baselines, accessibility, auditability, approved hosting environments, retention policies, and procurement-aware technology choices.

### Education

The Education profile should favor accessibility, privacy for minors where applicable, role separation, content management, and cost-conscious deployment.

### FinTech

The FinTech profile should favor auditability, strong authorization, transaction integrity, observability, security scanning, compliance posture, and careful third-party integration.

### Profile and Template Interaction

Profiles and templates operate at different layers:

- Template answers "what kind of product is this?"
- Profile answers "what engineering standards must this organization follow?"

When both provide defaults, the organization profile should have higher policy authority, while the template provides domain-specific defaults within those constraints. Conflicts must be reported. The user may override template defaults freely, but profile overrides may require explicit acknowledgment or administrative permission depending on future policy design.

## 12. Validation Engine

The Validation Engine ensures PlanningSelections is complete, coherent, supported, and ready for downstream generation.

Validation responsibilities include:

- Missing required selections.
- Mutually exclusive technologies.
- Dependency validation.
- Deprecated technologies.
- Unsupported combinations.
- Policy violations.
- Incomplete custom requirements.
- Capability pack prerequisites.
- Profile-template conflicts.
- Security and compliance gaps.
- Renderer-independent error reporting.

### Missing Required Selections

The engine should identify required decisions based on selected template, profile, packs, and workflow. A blank project may require fewer decisions than an enterprise healthcare project. Missing decisions should be grouped by section and severity.

### Mutually Exclusive Technologies

The engine should detect selections that cannot coexist. For example, two primary backend frameworks may conflict unless the architecture explicitly supports multiple services. Two incompatible deployment targets may conflict unless multi-environment deployment is selected.

### Dependency Validation

The engine should verify all required dependencies are selected or intentionally resolved. It should also surface recommended dependencies without blocking unless the rule is marked required.

### Deprecated Technologies

The engine should warn or block deprecated technologies depending on severity, profile policy, and plugin metadata. Deprecation messages should include replacement suggestions.

### Unsupported Combinations

The engine should block combinations that the platform cannot generate or validate. Unsupported does not mean impossible in the real world; it means Sohail-Agent-CLI cannot safely generate that combination yet.

### Conflict Reporting

Conflict reports should be actionable. Each report should include:

- Conflict summary.
- Affected decisions.
- Severity.
- Source rule.
- Explanation.
- Suggested resolutions.
- Whether the conflict blocks generation.

The engine should support validation states such as valid, valid with warnings, blocked, and incomplete.

## 13. Renderer Abstraction

The Engineering Decision Engine must not depend on CLI behavior. CLI is one renderer, not the engine.

The engine should expose renderer-neutral planning sessions. A renderer receives question definitions, displays them appropriately, returns answers, and presents validation results. The engine owns decision state, progression, validation, defaults, dependencies, and final output.

Future renderers:

- CLI.
- Terminal UI.
- Web UI.
- Desktop UI.
- VS Code Extension.
- API.

### CLI Renderer

The CLI renderer should support command-line workflows, prompts, flags, non-interactive defaults, and scriptable execution.

### Terminal UI Renderer

The Terminal UI renderer should support richer navigation, grouped sections, review screens, progress indicators, and inline validation.

### Web UI Renderer

The Web UI renderer should support forms, guided flows, contextual help, collaborative review, saved sessions, and richer recommendation displays.

### Desktop UI Renderer

The Desktop UI renderer should support local project integration, file pickers, visual review, and multi-agent orchestration.

### VS Code Extension Renderer

The VS Code renderer should support workspace-aware decisions, repository context, inline warnings, and generation actions from the editor.

### API Renderer

The API renderer should support automation, enterprise workflows, external frontends, and non-interactive planning sessions.

All renderers must use the same engine semantics. A decision captured in the CLI should be equivalent to one captured in the web UI. Renderer differences should affect presentation only, not validation, defaults, or final PlanningSelections.

## 14. Plugin Architecture

The Plugin Architecture allows EDE to grow without modifying the core repository for every new domain, technology, organization standard, or validation rule.

Future plugins should register:

- Questions.
- Templates.
- Technology options.
- Capability packs.
- Validation rules.
- Profiles.

Plugin contributions should include metadata:

- Plugin identifier.
- Version.
- Namespace.
- Supported engine version.
- Provided sections.
- Provided options.
- Provided rules.
- Dependencies on other plugins.
- Deprecation status.

### Questions

Plugins may add questions to existing sections or define plugin-owned sections. Plugin questions must use standard question types and validation metadata.

### Templates

Plugins may add project templates for specialized domains such as legal technology, real estate, logistics, media platforms, or internal enterprise systems.

### Technology Options

Plugins may add frameworks, databases, cloud providers, monitoring tools, AI providers, or deployment targets. Technology options must declare compatibility metadata and downstream generation support.

### Capability Packs

Plugins may add reusable capability bundles. Examples include geospatial features, document workflows, marketplace features, enterprise SSO, or data pipelines.

### Validation Rules

Plugins may add validation rules. Rules must be explainable, deterministic, and scoped to known decisions. Plugin rules should not silently rewrite selections.

### Profiles

Plugins may add organization profiles for companies, industries, teams, or regulatory environments.

The core engine should treat plugin contributions as registered decision vocabulary. It should validate plugin metadata before using it and isolate plugin namespaces to prevent accidental collisions.

## 15. AI Interaction Philosophy

AI is an engineering advisor.

AI may:

- Recommend.
- Explain.
- Warn.
- Review.
- Compare tradeoffs.
- Identify missing decisions.
- Suggest capability packs.
- Suggest validation improvements.
- Summarize selected decisions.

AI must not:

- Invent requirements.
- Override user choices.
- Silently change architecture.
- Add dependencies without approval.
- Change selected technologies without approval.
- Convert recommendations into final decisions automatically.
- Hide uncertainty.
- Bypass validation.

This philosophy is fundamental to EDE. AI should make the user more informed, not less in control. The engine should treat AI output as advisory input that requires explicit disposition. Accepted AI suggestions become normal decisions with provenance. Rejected or deferred suggestions remain separate from final selections.

Downstream agents should receive user-approved decisions, not raw AI speculation. If AI participates in later generation stages, it must operate inside the boundaries established by PlanningSelections.

## 16. Future Roadmap

The Engineering Decision Engine enables a broader evolution of Sohail-Agent-CLI from individual generation agents into a decision-driven engineering platform.

### PlanningAgent V2

PlanningAgent V2 should become the primary user-facing entry point for EDE. It should guide users through templates, profiles, capability packs, explicit questions, recommendations, validation, review, and planning package generation.

### ImplementationAgent

ImplementationAgent can use PlanningSelections to generate application code within approved architecture, stack, dependencies, security posture, and custom requirements. It should fail when requested implementation work exceeds approved decisions.

### TestingAgent

TestingAgent can derive test strategy, frameworks, coverage goals, acceptance criteria, and custom requirement tests from PlanningSelections. It can ensure generated tests reflect approved quality expectations.

### DeploymentAgent

DeploymentAgent can consume cloud, containerization, CI/CD, secrets, monitoring, and environment decisions. It can generate deployment assets without guessing provider or runtime choices.

### ReviewAgent

ReviewAgent can compare generated artifacts against PlanningSelections. It can identify drift, missing requirements, unsupported implementation choices, security gaps, and documentation mismatches.

### Future Web UI

A web UI can present EDE as a guided planning workspace with templates, profiles, decision review, AI recommendations, validation reports, and collaboration workflows.

### Future Desktop Application

A desktop application can integrate local repositories, planning sessions, generation runs, visual file review, and agent orchestration while using the same engine as CLI and web renderers.

### Future Enterprise Edition

An enterprise edition can add organization-managed profiles, approved technology catalogs, policy enforcement, audit trails, team collaboration, private plugins, centralized planning records, and governance workflows.

## Closing Architecture Position

The Engineering Decision Engine should be the planning brain of Sohail-Agent-CLI. Its core responsibility is not to generate files. Its responsibility is to capture, validate, explain, and persist engineering decisions before generation begins.

The long-term health of the platform depends on keeping this boundary clear:

- EDE decides what is approved.
- Downstream agents generate from what is approved.
- AI advises but does not decide.
- Renderers display but do not own engine logic.
- Plugins extend but do not bypass validation.

This architecture makes future generation more deterministic, more maintainable, more auditable, and more trustworthy.
