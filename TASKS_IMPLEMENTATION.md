# Sohail-Agent-CLI Implementation Roadmap

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
