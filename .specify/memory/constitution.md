<!--
Sync Impact Report:
Version: 0.0.0 → 1.0.0
Rationale: Initial constitution creation (MAJOR version for first release)

Modified Principles: N/A (initial creation)
Added Sections:
  - All core principles (1-7)
  - Deep Agent Architecture Constraints
  - Development Workflow
  - Governance

Removed Sections: N/A (initial creation)

Templates Status:
  ✅ .specify/templates/plan-template.md - Constitution Check section aligned
  ✅ .specify/templates/spec-template.md - Requirements structure aligned
  ✅ .specify/templates/tasks-template.md - Task categorization aligned

Follow-up TODOs: None
-->

# Deep Agents Project Constitution

## Core Principles

### I. Middleware-First Architecture

Every feature and capability in Deep Agents MUST be implemented as composable middleware. Middleware provides modular, reusable functionality that can be attached to agents independently.

**Rules**:

- New capabilities MUST be implemented as AgentMiddleware subclasses
- Middleware MUST be independently testable
- Middleware MUST NOT have circular dependencies
- Core functionality (planning, filesystem, subagents) remains as built-in middleware

**Rationale**: Middleware architecture enables users to compose exactly the capabilities they need, reduces complexity, and ensures modularity. This is fundamental to the "general purpose" nature of Deep Agents.

### II. Backward Compatibility

Public APIs MUST maintain backward compatibility within major versions. Breaking changes require major version bumps and clear migration guides.

**Rules**:

- `create_deep_agent` signature changes require major version bump
- Middleware interfaces cannot change within major versions
- Deprecation warnings MUST precede removal by at least one minor version
- All breaking changes MUST be documented in migration guides

**Rationale**: Deep Agents is a library used in production. Users must be able to upgrade with confidence that their code will continue to work.

### III. Framework Agnostic (LangGraph Native)

Deep Agents MUST remain a pure LangGraph extension. All agents created are standard LangGraph graphs with no proprietary abstractions.

**Rules**:

- Return types MUST be standard LangGraph CompiledGraph objects
- State management MUST use LangGraph's StateGraph
- Checkpointing MUST use LangGraph's Checkpointer interface
- Store MUST use LangGraph's Store interface
- NO custom wrappers that hide LangGraph concepts

**Rationale**: Users get full access to LangGraph's ecosystem (streaming, human-in-the-loop, Studio, deployment) without learning a new framework. Deep Agents enhances rather than replaces LangGraph.

### IV. Model Agnostic

Deep Agents MUST support any LangChain-compatible chat model. Default to Claude Sonnet 4.5 but impose no model restrictions.

**Rules**:

- Model parameter accepts any BaseChatModel instance
- NO model-specific features in core library
- Default model can be specified via string (e.g., "anthropic:claude-sonnet-4-20250514")
- Documentation MUST show examples with multiple providers

**Rationale**: Users should choose models based on their needs (cost, performance, compliance). Vendor lock-in reduces adoption and limits use cases.

### V. Test Coverage for Core Features

Core middleware (TodoList, Filesystem, SubAgent) MUST maintain high test coverage. New middleware contributions encouraged but not required to have tests initially.

**Rules**:

- Core middleware MUST have integration tests
- Core middleware MUST have contract tests for tool schemas
- Bug fixes MUST include regression tests
- Breaking changes MUST update all affected tests

**Rationale**: Core features are foundational to Deep Agents. Comprehensive testing prevents regressions and ensures reliability for all users.

### VI. Clear, Comprehensive Documentation

Every feature MUST be documented with purpose, usage examples, and best practices. Documentation targets both library users and contributors.

**Rules**:

- New middleware MUST include docstrings and README examples
- Complex features MUST have dedicated documentation files in docs/
- API changes MUST update relevant documentation
- Examples MUST be runnable and tested

**Rationale**: Deep Agents implements complex patterns (subagents, parallelization, context management). Clear documentation is essential for adoption and effective use.

### VII. Performance and Cost Consciousness

Features MUST consider token usage, latency, and API costs. Provide optimization options without forcing them.

**Rules**:

- Middleware MUST document token/cost implications
- Provide opt-in optimizations (caching, summarization)
- Examples MUST show both basic and optimized patterns
- Performance guidance in documentation

**Rationale**: Agents can be expensive to run at scale. Users need visibility into costs and tools to optimize. Default to simplicity, offer optimization paths.

## Deep Agent Architecture Constraints

**Purpose**: Maintain the integrity of the "Deep Agent" pattern while allowing flexibility.

### Four Pillars (Non-negotiable)

Deep Agents MUST provide these capabilities, implemented via middleware:

1. **Planning Tool** (TodoListMiddleware)
   - `write_todos` tool for task decomposition
   - Progress tracking and adaptive planning

2. **Filesystem** (FilesystemMiddleware)
   - Context offloading to prevent overflow
   - Short-term (state) and long-term (store) memory
   - Tools: ls, read_file, write_file, edit_file

3. **Subagents** (SubAgentMiddleware)
   - Context isolation via task delegation
   - Parallel execution of independent tasks
   - Support for specialized and general-purpose subagents

4. **Detailed Prompts**
   - Comprehensive system_prompt parameter
   - Clear instructions for middleware usage
   - Best practices guidance in prompts

### Optional Enhancements

Additional middleware can be added but MUST NOT be required:

- SummarizationMiddleware
- AnthropicPromptCachingMiddleware
- HumanInTheLoopMiddleware
- Custom user middleware

**Rationale**: These four capabilities define what makes an agent "deep" per the research that inspired this library (Claude Code, Deep Research, Manus). They must remain core while allowing extensibility.

## Development Workflow

**Purpose**: Ensure quality and consistency across contributions.

### Code Quality Gates

- **Linting**: All code MUST pass `ruff check` with project configuration
- **Formatting**: All code MUST be formatted with `ruff format`
- **Type Checking**: Core library SHOULD pass `mypy --strict` (best effort)
- **Line Length**: Maximum 150 characters per line

### Contribution Process

1. **Issues First**: Discuss significant changes in GitHub issues before implementation
2. **Branch Naming**: Use descriptive names (e.g., `feature/custom-middleware`, `fix/filesystem-bug`)
3. **Commit Messages**: Clear, descriptive commits following conventional commits style
4. **Pull Requests**: Include description, test evidence, documentation updates
5. **Review**: At least one maintainer approval required

### Testing Strategy

- **Unit Tests**: For isolated functionality
- **Integration Tests**: For middleware interactions
- **Contract Tests**: For tool schemas and interfaces
- **Example Tests**: Ensure examples run successfully

### Version Bumping

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes to public APIs
- **MINOR**: New features, new middleware, backward-compatible additions
- **PATCH**: Bug fixes, documentation, non-breaking improvements

## Governance

**Purpose**: Maintain project direction and quality standards.

### Amendment Process

1. Propose change via GitHub issue with "constitution" label
2. Discuss rationale, impact, and alternatives
3. Require maintainer consensus (2+ maintainers for controversial changes)
4. Document in constitution with version bump
5. Update affected templates and documentation
6. Announce in release notes

### Principle Priority

When in conflict, principles are prioritized as:

1. Framework Agnostic (LangGraph Native) - Core identity
2. Backward Compatibility - User trust
3. Middleware-First Architecture - Technical foundation
4. Model Agnostic - User freedom
5. Test Coverage - Quality
6. Documentation - Adoption
7. Performance/Cost - Optimization

### Compliance Review

- Pull requests MUST be checked against constitution
- Violations MUST be justified or fixed
- Maintainers enforce compliance during code review
- Major contributions reviewed against all principles

### Complexity Justification

Violations of simplicity/modularity principles MUST be justified:

- Why is this complexity necessary?
- What simpler alternative was considered?
- What is the maintenance burden?
- Can it be made optional?

**Version**: 1.0.0 | **Ratified**: 2025-11-03 | **Last Amended**: 2025-11-03
