---
allowed-tools: Task, Read, Glob, Grep
argument-hint: [prd-path] [research-path]
description: SPICE design — spawn isolated subagent to create Technical Design Document
---

# SPICE Design

**PRD**: $1
**Research**: $2

This command spawns an **isolated subagent** to create a Technical Design Document (TDD).

The TDD is the technical counterpart to the PRD — it translates requirements into architecture, data models, API contracts, and technical decisions.

---

## Process

### 1. Validate Inputs

Verify both files exist:
- PRD document at $1
- Research document at $2

Derive context folder from the PRD path.

### 2. Spawn Designer Subagent

**Use the Task tool** to spawn the `spice-designer` agent:

```
Task tool:
  agent: spice-designer
  prompt: |
    PRD: $1
    Research: $2
    Context folder: {derived from PRD path}
    
    Execute the designer protocol.
    
    1. Read PRD and research documents
    2. Define system architecture with components
    3. Design data models with entities and relationships
    4. Specify API contracts with request/response formats
    5. Document technical decisions with rationale
    6. Define interfaces, protocols, and error types
    
    Write output to: {context_folder}/tdd-001.md
    
    CRITICAL sections to include:
    - Architecture (components, interactions)
    - Data Models (entities, relationships, schemas)
    - API Contracts (endpoints, requests, responses, errors)
    - Interfaces (service protocols, DTOs)
    - Technical Decisions (choices with rationale)
    - Security Considerations
```

### 3. Review Output

After subagent completes:
- Summarize the technical approach
- Highlight key decisions
- Note any open questions
- Suggest next step: `/spice:plan`

---

## TDD vs PRD

| PRD (Product) | TDD (Technical) |
|---------------|-----------------|
| What to build | How to build it |
| User stories | System architecture |
| Functional requirements | API contracts |
| Success metrics | Performance considerations |
| Non-goals | Technical decisions |

---

## When to Use

### Always Create TDD For:
- New services or major components
- API design (internal or external)
- Database schema changes
- Integration with external systems
- Features requiring technical decisions

### Skip TDD For:
- Simple bug fixes
- UI-only changes with no backend
- Configuration changes
- Documentation updates

---

## Next Step

After TDD approval, create the implementation plan:
```bash
/spice:plan {context_folder}/prd-001.md {context_folder}/tdd-001.md
```

Note: The planner reads BOTH PRD and TDD to create comprehensive tasks.

---

## Examples

```bash
# Standard design phase
/spice:design /context/001-auth/prd-001.md /context/001-auth/research-001.md

# After completing research
/spice:design /context/002-payments/prd-001.md /context/002-payments/research-001.md
```
