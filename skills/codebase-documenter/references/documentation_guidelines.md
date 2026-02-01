# Documentation Guidelines

This reference provides comprehensive best practices and style guidelines for creating high-quality documentation.

## Writing Style Guide

### Voice and Tone

**Use active voice:**
- ✅ "The function returns a user object"
- ❌ "A user object is returned by the function"

**Be direct and concise:**
- ✅ "Install dependencies with `npm install`"
- ❌ "You can install the dependencies by running the npm install command"

**Use present tense:**
- ✅ "The API returns an error when..."
- ❌ "The API will return an error when..."

**Avoid unnecessary words:**
- ✅ "To start the server, run..."
- ❌ "In order to start the server, you will need to run..."

### Technical Writing Conventions

**Code formatting:**
- Use backticks for inline code: `variable`, `function()`, `npm install`
- Use code blocks for multi-line code with language specification
- Include command prompts (`$`, `>`) only when necessary for clarity

**Capitalization:**
- Use sentence case for headings: "Getting started" not "Getting Started"
- Capitalize proper nouns: "Docker", "PostgreSQL", "JavaScript"
- Lowercase for commands and file names: `npm`, `package.json`, `index.js`

**Punctuation:**
- Use periods for complete sentences
- No periods for list items that aren't complete sentences
- Use serial comma: "red, white, and blue"

**Lists:**
- Use numbered lists for sequential steps
- Use bullet lists for non-sequential items
- Indent sub-items consistently

## Structure Patterns

### Progressive Disclosure

Organize information from simple to complex:

```markdown
## Getting Started

[Basic usage example that works immediately]

## Core Concepts

[Key concepts needed to understand the system]

## Advanced Usage

[Complex scenarios and edge cases]

## API Reference

[Complete technical reference]
```

### Task-Oriented Structure

Organize by what users want to accomplish:

```markdown
## Common Tasks

### Adding a new feature
[Step-by-step instructions]

### Debugging issues
[Troubleshooting guide]

### Deploying to production
[Deployment instructions]
```

### The "Five-Minute Rule"

Every project should have a path that gets users to success in under 5 minutes:

1. **Quick Start** section at the top
2. Minimal setup steps
3. One working example
4. Clear success indicator ("You should see...")
5. Link to deeper docs for next steps

## Content Guidelines

### Code Examples

**Make examples realistic:**
- ✅ Use real-world variable names and scenarios
- ❌ Don't use `foo`, `bar`, `baz` unless explaining general concepts

```javascript
// ✅ GOOD: Realistic example
const user = await fetchUser('usr_123');
if (user.role === 'admin') {
  showAdminPanel();
}

// ❌ BAD: Unclear example
const foo = await bar('baz');
if (foo.x === 'y') {
  doThing();
}
```

**Include context:**
```javascript
// ✅ GOOD: Shows where this code lives
// src/services/auth.js

export async function login(email, password) {
  // Implementation
}

// ❌ BAD: No context about where to put this
async function login(email, password) {
  // Implementation
}
```

**Show complete examples:**
```javascript
// ✅ GOOD: Complete, runnable example
import { createUser } from './services/user';

async function example() {
  try {
    const user = await createUser({
      name: 'John Doe',
      email: 'john@example.com'
    });
    console.log('User created:', user.id);
  } catch (error) {
    console.error('Failed to create user:', error);
  }
}

// ❌ BAD: Incomplete example
const user = await createUser({...});
```

### Error Documentation

**Document error messages:**
```markdown
### Common Errors

**Error: `ECONNREFUSED`**
- **Cause:** Database is not running
- **Solution:** Start the database with `docker-compose up -d postgres`
- **Prevention:** Run `docker-compose up -d` before starting the app

**Error: `Port 3000 is already in use`**
- **Cause:** Another process is using port 3000
- **Solution:** Kill the process with `lsof -ti:3000 | xargs kill -9`
- **Prevention:** Configure a different port in `.env` file
```

### Prerequisites and Dependencies

**Be explicit about requirements:**
```markdown
## Prerequisites

Before starting, ensure you have:

- **Node.js 18 or higher** - Check with `node --version`
  - Download from https://nodejs.org
  - Recommended: Use nvm for version management

- **PostgreSQL 14+** - Check with `psql --version`
  - macOS: `brew install postgresql`
  - Ubuntu: `sudo apt-get install postgresql`
  - Windows: Download from https://postgresql.org/download

- **API keys** - Required for authentication
  - Sign up at https://example.com/api
  - Create new API key in dashboard
  - Save key securely (you'll need it in setup)
```

### Configuration Documentation

**Document all configuration options:**

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `PORT` | number | No | `3000` | Port for the server to listen on |
| `DATABASE_URL` | string | Yes | - | PostgreSQL connection string |
| `NODE_ENV` | enum | No | `development` | Environment mode (`development`, `production`, `test`) |
| `LOG_LEVEL` | enum | No | `info` | Logging verbosity (`error`, `warn`, `info`, `debug`) |
| `API_KEY` | string | Yes | - | Third-party API authentication key |

**Include examples:**
```bash
# Development
PORT=3000
DATABASE_URL=postgresql://localhost:5432/myapp_dev
NODE_ENV=development
LOG_LEVEL=debug
API_KEY=sk_test_123abc

# Production
PORT=8080
DATABASE_URL=postgresql://prod.example.com:5432/myapp
NODE_ENV=production
LOG_LEVEL=info
API_KEY=sk_live_789xyz
```

## Visual Aids

### File Tree Structures

Use ASCII art for directory structures:

```
project/
├── src/
│   ├── components/
│   │   ├── Button.tsx       # Reusable button component
│   │   └── Modal.tsx        # Reusable modal component
│   ├── pages/
│   │   ├── Home.tsx         # Home page component
│   │   └── About.tsx        # About page component
│   └── utils/
│       └── format.ts        # Formatting utilities
├── tests/
│   └── components/
│       └── Button.test.tsx  # Button component tests
└── package.json             # Dependencies and scripts
```

### Diagrams

Use ASCII diagrams for flows and relationships:

```
Authentication Flow:

User                     Frontend                 Backend                 Database
  |                         |                        |                        |
  |--- Submit Credentials-->|                        |                        |
  |                         |--- POST /auth/login -->|                        |
  |                         |                        |--- Query User -------->|
  |                         |                        |<------ User Data ------|
  |                         |                        |                        |
  |                         |                        |--- Verify Password --->|
  |                         |                        |<------ Result ---------|
  |                         |                        |                        |
  |                         |<------ JWT Token ------|                        |
  |<-- Login Success -------|                        |                        |
  |                         |                        |                        |
```

### Tables for Comparisons

Use tables to compare options:

| Feature | Option A | Option B | Option C |
|---------|----------|----------|----------|
| Performance | Fast | Medium | Slow |
| Ease of use | Complex | Simple | Medium |
| Flexibility | High | Low | Medium |
| Best for | Large projects | Prototypes | Medium projects |

## Accessibility

### Write for Screen Readers

- Use semantic markdown headings (`#`, `##`, `###`)
- Provide alt text for images: `![Diagram showing data flow](diagram.png)`
- Use descriptive link text: ✅ "Read the API documentation" vs ❌ "Click here"

### Support Multiple Learning Styles

Provide information in multiple formats:

1. **Visual:** Diagrams, screenshots, file trees
2. **Textual:** Written explanations, code comments
3. **Interactive:** Working examples, commands to try

## Maintenance

### Keep Documentation Current

**Add version information:**
```markdown
> **Note:** This documentation is for version 2.x. For version 1.x documentation, see [v1 docs](./v1/README.md).

Last updated: 2024-01-15
```

**Mark deprecated features:**
```markdown
## ⚠️ Deprecated: `legacyAuth()`

**Deprecated in:** v2.0.0
**Removed in:** v3.0.0
**Alternative:** Use `modernAuth()` instead

```javascript
// ❌ Old way (deprecated)
await legacyAuth(token);

// ✅ New way
await modernAuth(token);
```
```

**Document breaking changes:**
```markdown
## Breaking Changes in v2.0

### Changed: Authentication method

**Before (v1.x):**
```javascript
auth.login(username, password);
```

**After (v2.x):**
```javascript
auth.login({ email, password });
```

**Migration guide:**
Replace `username` with `email` and wrap parameters in an object.
```

## Documentation Types

### README Documentation

**Essential sections:**
1. What this does (1-2 sentences)
2. Quick start (< 5 minutes to running)
3. Project structure (visual overview)
4. Common tasks (step-by-step guides)
5. Configuration (environment variables, settings)
6. Troubleshooting (common issues)
7. Links to additional docs

**Keep it focused:**
- Root README should be high-level
- Link to detailed docs in subdirectories
- Aim for 500-1000 words max

### Architecture Documentation

**Essential sections:**
1. System design (high-level overview)
2. Directory structure (detailed breakdown)
3. Data flow (how data moves through system)
4. Key design decisions (why choices were made)
5. Module dependencies (how components interact)
6. Extension points (where to add features)

**Document the "why":**
- Explain architectural decisions
- Provide context for choices made
- Document alternatives considered
- Note trade-offs accepted

### API Documentation

**Essential sections:**
1. Authentication (how to authenticate)
2. Error handling (error format and codes)
3. Rate limiting (limits and headers)
4. Endpoints (all available endpoints)
5. Examples (realistic usage examples)

**For each endpoint:**
- What it does (plain-English explanation)
- Authentication requirements
- Request format (parameters, body)
- Response format (success and errors)
- Working example (curl or SDK)
- Common errors (what can go wrong)

### Inline Code Documentation

**Essential elements:**
1. Purpose (why this code exists)
2. Parameters (what inputs mean)
3. Return value (what output means)
4. Examples (how to use it)
5. Edge cases (special behavior)

**Comment style:**
- Use standard format (JSDoc, docstrings, etc.)
- Explain "why" not "what"
- Include examples for complex functions
- Document assumptions and constraints

## Testing Documentation

**Test all code examples:**
- Verify commands actually work
- Test setup instructions on clean environment
- Check that links aren't broken
- Validate code snippets compile/run

**Make documentation testable:**
```markdown
<!-- Example that can be tested automatically -->
```bash
npm install
npm test
# Expected output: All tests passed (10 tests)
```
```

## Documentation Review Checklist

Before publishing documentation, verify:

**Completeness:**
- [ ] All required sections included
- [ ] Prerequisites clearly listed
- [ ] Setup steps are complete
- [ ] Examples are realistic and tested
- [ ] Links work correctly

**Clarity:**
- [ ] Written for target audience
- [ ] Technical terms defined
- [ ] Examples include context
- [ ] Success criteria clear

**Accuracy:**
- [ ] Code examples work
- [ ] Commands produce expected output
- [ ] Version numbers correct
- [ ] Links point to correct locations

**Organization:**
- [ ] Logical information flow
- [ ] Progressive disclosure used
- [ ] Related topics linked
- [ ] Visual aids where helpful

**Maintenance:**
- [ ] Last updated date included
- [ ] Version information noted
- [ ] Deprecated features marked
- [ ] Breaking changes documented

## Anti-Patterns to Avoid

**Don't assume knowledge:**
- ❌ "Just use the standard approach"
- ✅ "Use dependency injection (see [guide](./di.md))"

**Don't use vague instructions:**
- ❌ "Configure the system appropriately"
- ✅ "Set `PORT=3000` in your `.env` file"

**Don't skip error handling:**
- ❌ Only show happy path examples
- ✅ Show both success and error handling

**Don't leave gaps:**
- ❌ "Install dependencies" → "Run the app"
- ✅ "Install dependencies" → "Configure environment" → "Run migrations" → "Run the app"

**Don't use jargon without explanation:**
- ❌ "Uses CRDT for eventual consistency"
- ✅ "Uses CRDT (Conflict-free Replicated Data Type) to ensure all users see the same data even when working offline"

## Internationalization

**Write for global audience:**
- Use international date format: 2024-01-15 (not 1/15/2024)
- Avoid idioms and colloquialisms
- Use simple sentence structure
- Define acronyms on first use

**Examples for clarity:**
```markdown
## Date Formatting

Dates should use ISO 8601 format: `YYYY-MM-DD`

Examples:
- January 15, 2024 → `2024-01-15`
- March 3, 2024 → `2024-03-03`
- December 25, 2024 → `2024-12-25`
```

## Summary

**Great documentation is:**
1. **Accurate** - Information is correct and up-to-date
2. **Complete** - No critical gaps in coverage
3. **Clear** - Easy to understand for target audience
4. **Organized** - Information is easy to find
5. **Tested** - Examples and instructions actually work
6. **Maintained** - Kept current as code changes
7. **Accessible** - Works for different learning styles
8. **Actionable** - Users can accomplish their goals

**Documentation serves users when it:**
- Gets them started quickly (< 5 minutes to success)
- Answers their questions (comprehensive coverage)
- Helps them when stuck (troubleshooting guides)
- Grows with them (beginner to advanced content)
- Stays current (regular updates and maintenance)
