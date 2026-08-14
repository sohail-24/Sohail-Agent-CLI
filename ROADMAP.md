# Sohail-Agent-CLI Roadmap

This document outlines the current project status, implementation plans, and future milestones.

---

# Project Status

## Version

- Package version: `2.0.0`
- Current architecture phase: Local AI Software Engineering Framework foundation

## Progress

Sohail-Agent-CLI now has deterministic project planning, bootstrap scaffolding, technology stack skeleton generation, and reusable AI orchestration infrastructure.

## Completed Modules

- PlanningAgent
- BootstrapAgent
- StackAgent
- AI Foundation
- Existing DevOps agents: inspect, dockerize, Kubernetes, CI/CD, docs, interview

## Current Subsystem

AI Foundation is complete. It provides reusable context, memory, prompt, provider, routing, validation, parsing, and orchestration primitives.

## Next Milestone

SpecificationAgent should consume project plans, PRDs, templates, or requirements and produce validated structured specifications through the AI Foundation.

## Overall Architecture

```text
CLI
  ↓
Agent
  ↓
Generator / AIOrchestrator
  ↓
Core Package / Domain Package
  ↓
Workers
```

The AI Foundation does not replace the existing architecture. It gives future agents a controlled way to use local AI while Python keeps ownership of workflow, validation, and safety.


---

# AI Foundation Implementation Summary

## Purpose

The AI Foundation adds reusable orchestration infrastructure for future Sohail-Agent-CLI engineering subsystems. It does not generate files directly, add business features, or change existing PlanningAgent, BootstrapAgent, or StackAgent behavior.

## Architecture

```text
Future Agent
  ↓
AIOrchestrator
  ↓
AIRouter
  ↓
PromptBuilder
  ↓
Provider
  ↓
AIResponseValidator
  ↓
AIResponseParser
  ↓
Dataclasses
```

## Execution Flow

1. A future agent creates an `AIRequest`.
2. `AIRouter` maps the request task to a prompt template.
3. `PromptBuilder` injects `ProjectContext`.
4. The selected provider executes inference.
5. `AIResponseValidator` rejects malformed or unsafe structure.
6. Invalid responses are retried within the configured retry limit.
7. `AIResponseParser` returns `AIStructuredOutput`.
8. `AIOrchestrator` returns `AIResult` with execution metadata.

## CLI Usage

There is no direct CLI command for the AI Foundation. It is an internal infrastructure layer for future agents.

## Public Classes

- `AIContextBuilder`
- `ProjectMemory`
- `PromptCatalog`
- `PromptBuilder`
- `AIProviderFactory`
- `AITaskRegistry`
- `AIRouter`
- `AIOrchestrator`
- `AIResponseValidator`
- `AIResponseParser`

## Dataclasses

- `ProjectContext`
- `PromptTemplate`
- `AIRequest`
- `AIStructuredOutput`
- `AIExecutionMetadata`
- `AIResult`
- `MemoryEntry`
- `ProviderSpec`
- `AIRoute`

## Responsibilities

- `src/ai/context.py`: builds normalized project context from `project-plan/`.
- `src/ai/memory.py`: stores serializable engineering memory.
- `src/ai/prompts.py`: owns versioned reusable prompts.
- `src/ai/provider.py`: selects supported providers and rejects placeholders.
- `src/ai/registry.py`: maps AI task names to prompt templates.
- `src/ai/router.py`: routes requests to prompts.
- `src/ai/orchestrator.py`: controls provider execution, validation, retries, and parsing.
- `src/ai/validator.py`: validates JSON, required fields, enums, unknown keys, empty responses, and malformed responses.
- `src/ai/response_parser.py`: converts validated response data into dataclasses.
- `src/ai/exceptions.py`: centralizes AI infrastructure exceptions.

## Integration Points

- Future agents can call `AIOrchestrator.execute()`.
- `AIContextBuilder` consumes PlanningAgent output.
- `AIProviderFactory` reuses existing `MockProvider` and `OllamaProvider`.
- Generators should consume parsed dataclasses only.

## Design Decisions

- No existing agents were rewired.
- No new CLI command was added.
- Cloud providers are placeholders, not partial implementations.
- The AI layer validates before parsing.
- Raw provider text is contained inside the orchestrator pipeline.

## Validation

- Full test suite passed in the implementation workspace.
- Added AI foundation tests for provider selection, mock provider behavior, context building, prompt building, router behavior, response parsing, validation, memory, and orchestrator retry behavior.

## Known Limitations

- Ollama is implemented through the existing provider but was not network-smoke-tested.
- Cloud providers are intentionally unsupported placeholders.
- The generic `AIStructuredOutput` model is intentionally broad; future subsystems should add domain-specific dataclasses.
- Existing agents do not yet consume the AI layer.

## Future Improvements

1. Add SpecificationAgent on top of `AIOrchestrator`.
2. Add domain-specific response schemas.
3. Add optional local Ollama smoke tests.
4. Add persisted AI memory files once a future agent owns lifecycle rules.


---


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


---

## Long-Term Implementation Roadmap

## Completed

- PlanningAgent ✅
- BootstrapAgent ✅
- StackAgent ✅
- AI Foundation ✅

## In Progress

- None

## Planned

- SpecificationAgent ⏳
- BlueprintAgent ⏳
- FeatureAgent ⏳
- FrontendAgent ⏳
- BackendAgent ⏳
- DatabaseAgent ⏳
- DockerAgent V2 ⏳
- KubernetesAgent V2 ⏳
- CI/CD V2 ⏳
- DocumentationAgent V2 ⏳
- InterviewAgent V2 ⏳

## Blocked

- Cloud provider integrations are blocked until a real subsystem requires them.
- Domain-specific AI response schemas are blocked until the next agent contract is designed.

## Technical Debt

- Existing direct CLI dispatch remains the current integration style.
- Existing providers do not yet expose provider-specific structured-output capabilities.
- Existing DevOps generators predate the Planning/Bootstrap/Stack/AI pipeline and may need future hardening.

## Current Task

AI Foundation implementation is complete and validated.

## Next Recommended Task

Design and implement SpecificationAgent using `AIOrchestrator`, `AIContextBuilder`, and validated dataclass outputs.


---

## Detailed Implementation Plan

## Current Phase

- **Phase:** AI Foundation
- **Status:** Implemented and validated
- **Architecture:** Existing `CLI → Agent → Generator → Core Package` is preserved
- **Implementation type:** Additive infrastructure
- **Provider behavior:** Existing providers remain compatible; AI foundation selects Mock or Ollama

## Objective

Add reusable AI orchestration infrastructure for future subsystems without changing the behavior of PlanningAgent, BootstrapAgent, StackAgent, or existing DevOps agents.

The AI foundation owns:

- prompt construction;
- context injection;
- provider selection;
- inference execution;
- response validation;
- retry handling;
- response parsing into dataclasses;
- lightweight serializable project memory.

## Architecture Decisions

1. Python controls workflow, validation, parsing, filesystem access, and safety.
2. Providers return text only; generators never consume raw AI text.
3. AI output must validate as a JSON object before parsing.
4. Parsed AI output is returned as dataclasses, not dictionaries.
5. Cloud providers remain explicit placeholders.
6. No CLI command was added for the AI foundation because it is reusable infrastructure.
7. Existing agents are not rewired to use AI yet.

## Files Created

- `src/ai/__init__.py`
- `src/ai/models.py`
- `src/ai/context.py`
- `src/ai/memory.py`
- `src/ai/prompts.py`
- `src/ai/provider.py`
- `src/ai/registry.py`
- `src/ai/router.py`
- `src/ai/orchestrator.py`
- `src/ai/response_parser.py`
- `src/ai/validator.py`
- `src/ai/exceptions.py`
- `tests/ai/test_context.py`
- `tests/ai/test_memory.py`
- `tests/ai/test_prompts.py`
- `tests/ai/test_router.py`
- `tests/ai/test_validator.py`
- `tests/ai/test_response_parser.py`
- `tests/ai/test_provider.py`
- `tests/ai/test_orchestrator.py`
- `tests/providers/test_mock_provider.py`
- `PROJECT_STATUS.md`
- `DEVELOPER_GUIDE.md`

## Files Modified

- `IMPLEMENTATION_PLAN.md`
- `IMPLEMENTATION_SUMMARY.md`
- `TASKS_IMPLEMENTATION.md`
- `README.md`

## Testing Strategy

- Unit-test each AI foundation component independently.
- Use `MockProvider` for deterministic orchestrator tests.
- Validate malformed, empty, unknown-key, missing-field, invalid-enum, and bad-type responses.
- Validate context loading against PlanningAgent-style `project-plan/`.
- Run the full repository suite after implementation.

## Remaining Roadmap

1. Wire future SpecificationAgent to AIOrchestrator.
2. Add BlueprintAgent after specification flow stabilizes.
3. Add structured response models per future subsystem.
4. Add optional Ollama smoke testing in local development documentation.
5. Keep cloud provider implementations postponed until a real subsystem needs them.

## Recommended Next Subsystem

**SpecificationAgent** should be next. It can consume PRDs, templates, or planning packages and produce validated structured specifications through the new AI foundation.
