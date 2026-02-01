---
name: codebase-documenter
description: This skill should be used when writing documentation for codebases, including README files, architecture documentation, code comments, and API documentation. Use this skill when users request help documenting their code, creating getting-started guides, explaining project structure, or making codebases more accessible to new developers. The skill provides templates, best practices, and structured approaches for creating clear, beginner-friendly documentation.
---

# Codebase Documenter

## Overview

This skill enables creating comprehensive, beginner-friendly documentation for codebases. It provides structured templates and best practices for writing READMEs, architecture guides, code comments, and API documentation that help new users quickly understand and contribute to projects.

## Core Principles for Beginner-Friendly Documentation

When documenting code for new users, follow these fundamental principles:

1. **Start with the "Why"** - Explain the purpose before diving into implementation details
2. **Use Progressive Disclosure** - Present information in layers from simple to complex
3. **Provide Context** - Explain not just what the code does, but why it exists
4. **Include Examples** - Show concrete usage examples for every concept
5. **Assume No Prior Knowledge** - Define terms and avoid jargon when possible
6. **Visual Aids** - Use diagrams, flowcharts, and file tree structures
7. **Quick Wins** - Help users get something running within 5 minutes

## Documentation Types and When to Use Them

### 1. README Documentation

**When to create:** For project root directories, major feature modules, or standalone components.

**Structure to follow:**
```markdown
# Project Name

## What This Does
[1-2 sentence plain-English explanation]

## Quick Start
[Get users running the project in < 5 minutes]

## Project Structure
[Visual file tree with explanations]

## Key Concepts
[Core concepts users need to understand]

## Common Tasks
[Step-by-step guides for frequent operations]

## Troubleshooting
[Common issues and solutions]
```

**Best practices:**
- Lead with the project's value proposition
- Include setup instructions that actually work (test them!)
- Provide a visual overview of the project structure
- Link to deeper documentation for advanced topics
- Keep the root README focused on getting started

### 2. Architecture Documentation

**When to create:** For projects with multiple modules, complex data flows, or non-obvious design decisions.

**Structure to follow:**
```markdown
# Architecture Overview

## System Design
[High-level diagram and explanation]

## Directory Structure
[Detailed breakdown with purpose of each directory]

## Data Flow
[How data moves through the system]

## Key Design Decisions
[Why certain architectural choices were made]

## Module Dependencies
[How different parts interact]

## Extension Points
[Where and how to add new features]
```

**Best practices:**
- Use diagrams to show system components and relationships
- Explain the "why" behind architectural decisions
- Document both the happy path and error handling
- Identify boundaries between modules
- Include visual file tree structures with annotations

### 3. Code Comments

**When to create:** For complex logic, non-obvious algorithms, or code that requires context.

**Annotation patterns:**

**Function/Method Documentation:**
```javascript
/**
 * Calculates the prorated subscription cost for a partial billing period.
 *
 * Why this exists: Users can subscribe mid-month, so we need to charge
 * them only for the days remaining in the current billing cycle.
 *
 * @param {number} fullPrice - The normal monthly subscription price
 * @param {Date} startDate - When the user's subscription begins
 * @param {Date} periodEnd - End of the current billing period
 * @returns {number} The prorated amount to charge
 *
 * @example
 * // User subscribes on Jan 15, period ends Jan 31
 * calculateProratedCost(30, new Date('2024-01-15'), new Date('2024-01-31'))
 * // Returns: 16.13 (17 days out of 31 days)
 */
```

**Complex Logic Documentation:**
```python
# Why this check exists: The API returns null for deleted users,
# but empty string for users who never set a name. We need to
# distinguish between these cases for the audit log.
if user_name is None:
    # User was deleted - log this as a security event
    log_deletion_event(user_id)
elif user_name == "":
    # User never completed onboarding - safe to skip
    continue
```

**Best practices:**
- Explain "why" not "what" - the code shows what it does
- Document edge cases and business logic
- Add examples for complex functions
- Explain parameters that aren't self-explanatory
- Note any gotchas or counterintuitive behavior

### 4. API Documentation

**When to create:** For any HTTP endpoints, SDK methods, or public interfaces.

**Structure to follow:**

```markdown
## Endpoint Name

### What It Does
[Plain-English explanation of the endpoint's purpose]

### Endpoint
`POST /api/v1/resource`

### Authentication
[What auth is required and how to provide it]

### Request Format
[JSON schema or example request]

### Response Format
[JSON schema or example response]

### Example Usage
[Concrete example with curl/code]

### Common Errors
[Error codes and what they mean]

### Related Endpoints
[Links to related operations]
```

**Best practices:**
- Provide working curl examples
- Show both success and error responses
- Explain authentication clearly
- Document rate limits and constraints
- Include troubleshooting for common issues

## Documentation Workflow

### Step 1: Analyze the Codebase

Before writing documentation:

1. **Identify entry points** - Main files, index files, app initialization
2. **Map dependencies** - How modules relate to each other
3. **Find core concepts** - Key abstractions users need to understand
4. **Locate configuration** - Environment setup, config files
5. **Review existing docs** - Build on what's there, don't duplicate

### Step 2: Choose Documentation Type

Based on user request and codebase analysis:

- **New project or missing README** → Start with README documentation
- **Complex architecture or multiple modules** → Create architecture documentation
- **Confusing code sections** → Add inline code comments
- **HTTP/API endpoints** → Write API documentation
- **Multiple types needed** → Address in order: README → Architecture → API → Comments

### Step 3: Generate Documentation

Use the templates from `assets/templates/` as starting points:

- `assets/templates/README.template.md` - For project READMEs
- `assets/templates/ARCHITECTURE.template.md` - For architecture docs
- `assets/templates/API.template.md` - For API documentation

Customize templates based on the specific codebase:

1. **Fill in project-specific information** - Replace placeholders with actual content
2. **Add concrete examples** - Use real code from the project
3. **Include visual aids** - Create file trees, diagrams, flowcharts
4. **Test instructions** - Verify setup steps actually work
5. **Link related docs** - Connect documentation pieces together

### Step 4: Review for Clarity

Before finalizing documentation:

1. **Read as a beginner** - Does it make sense without project context?
2. **Check completeness** - Are there gaps in the explanation?
3. **Verify examples** - Do code examples actually work?
4. **Test instructions** - Can someone follow the setup steps?
5. **Improve structure** - Is information easy to find?

## Documentation Templates

This skill includes several templates in `assets/templates/` that provide starting structures:

### Available Templates

- **README.template.md** - Comprehensive README structure with sections for quick start, project structure, and common tasks
- **ARCHITECTURE.template.md** - Architecture documentation template with system design, data flow, and design decisions
- **API.template.md** - API endpoint documentation with request/response formats and examples
- **CODE_COMMENTS.template.md** - Examples and patterns for effective inline documentation

### Using Templates

1. **Read the appropriate template** from `assets/templates/`
2. **Customize for the specific project** - Replace placeholders with actual information
3. **Add project-specific sections** - Extend the template as needed
4. **Include real examples** - Use actual code from the codebase
5. **Remove irrelevant sections** - Delete parts that don't apply

## Best Practices Reference

For detailed documentation best practices, style guidelines, and advanced patterns, refer to:

- `references/documentation_guidelines.md` - Comprehensive style guide and best practices
- `references/visual_aids_guide.md` - How to create effective diagrams and file trees

Load these references when:
- Creating documentation for complex enterprise codebases
- Dealing with multiple stakeholder requirements
- Needing advanced documentation patterns
- Standardizing documentation across a large project

## Common Patterns

### Creating File Tree Structures

File trees help new users understand project organization:

```
project-root/
├── src/                    # Source code
│   ├── components/        # Reusable UI components
│   ├── pages/             # Page-level components (routing)
│   ├── services/          # Business logic and API calls
│   ├── utils/             # Helper functions
│   └── types/             # TypeScript type definitions
├── public/                # Static assets (images, fonts)
├── tests/                 # Test files mirroring src structure
└── package.json           # Dependencies and scripts
```

### Explaining Complex Data Flows

Use numbered steps with diagrams:

```
User Request Flow:
1. User submits form → 2. Validation → 3. API call → 4. Database → 5. Response

[1] components/UserForm.tsx
    ↓ validates input
[2] services/validation.ts
    ↓ sends to API
[3] services/api.ts
    ↓ queries database
[4] Database (PostgreSQL)
    ↓ returns data
[5] components/UserForm.tsx (updates UI)
```

### Documenting Design Decisions

Capture the "why" behind architectural choices:

```markdown
## Why We Use Redux

**Decision:** State management with Redux instead of Context API

**Context:** Our app has 50+ components that need access to user
authentication state, shopping cart, and UI preferences.

**Reasoning:**
- Context API causes unnecessary re-renders with this many components
- Redux DevTools helps debug complex state changes
- Team has existing Redux expertise

**Trade-offs:**
- More boilerplate code
- Steeper learning curve for new developers
- Worth it for: performance, debugging, team familiarity
```

## Output Guidelines

When generating documentation:

1. **Write for the target audience** - Adjust complexity based on whether documentation is for beginners, intermediate, or advanced users
2. **Use consistent formatting** - Follow markdown conventions, consistent heading hierarchy
3. **Provide working examples** - Test all code snippets and commands
4. **Link between documents** - Create a documentation navigation structure
5. **Keep it maintainable** - Documentation should be easy to update as code changes
6. **Add dates and versions** - Note when documentation was last updated

## Quick Reference

**Command to generate README:**
"Create a README file for this project that helps new developers get started"

**Command to document architecture:**
"Document the architecture of this codebase, explaining how the different modules interact"

**Command to add code comments:**
"Add explanatory comments to this file that help new developers understand the logic"

**Command to document API:**
"Create API documentation for all the endpoints in this file"
