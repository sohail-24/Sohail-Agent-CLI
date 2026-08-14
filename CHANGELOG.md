# Changelog

All notable changes to the Sohail-Agent-CLI project will be documented in this file.

## [2.0.0] - Foundation Update
### Added
- Multi-agent orchestration layer (Registry, Router, Planner).
- AI Foundation supporting Providers (`OllamaProvider`, `MockProvider`).
- Safe execution Worker layer with `--dry-run` and `--overwrite` features.
- DevOps agents capabilities (inspect, dockerize, k8s, cicd, docs, interview).
- PlanningAgent, BootstrapAgent, and StackAgent functionalities.

### Changed
- Shifted architecture to explicit execution flow: `CLI → Agent → Generator → Worker`.
- Formalized project name to **Sohail-Agent-CLI**.
- Consolidated project files into a cleaner structure.
