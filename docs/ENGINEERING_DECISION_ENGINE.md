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
