---
name: conventional-commits
description: Format commit messages using the Conventional Commits specification. Use when creating commits, writing commit messages, or when the user mentions commits, git commits, or commit messages. Ensures commits follow the standard format for automated tooling, changelog generation, and semantic versioning.
license: MIT
metadata:
  author: github.com/bastos
  version: "2.0"
---

# Conventional Commits

Format all commit messages according to the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. This enables automated changelog generation, semantic versioning, and better commit history.

## Format Structure

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Commit Types

### Required Types

- **`feat:`** - A new feature (correlates with MINOR in Semantic Versioning)
- **`fix:`** - A bug fix (correlates with PATCH in Semantic Versioning)

### Common Additional Types

- **`docs:`** - Documentation only changes
- **`style:`** - Code style changes (formatting, missing semicolons, etc.)
- **`refactor:`** - Code refactoring without bug fixes or new features
- **`perf:`** - Performance improvements
- **`test:`** - Adding or updating tests
- **`build:`** - Build system or external dependencies changes
- **`ci:`** - CI/CD configuration changes
- **`chore:`** - Other changes that don't modify src or test files
- **`revert:`** - Reverts a previous commit

## Scope

An optional scope provides additional contextual information about the section of the codebase:

```
feat(parser): add ability to parse arrays
fix(auth): resolve token expiration issue
docs(readme): update installation instructions
```

## Description

- Must immediately follow the colon and space after the type/scope
- Use imperative mood ("add feature" not "added feature" or "adds feature")
- Don't capitalize the first letter
- No period at the end
- Keep it concise (typically 50-72 characters)

## Body

- Optional longer description providing additional context
- Must begin one blank line after the description
- Can consist of multiple paragraphs
- Explain the "what" and "why" of the change, not the "how"

## Breaking Changes

Breaking changes can be indicated in two ways:

### 1. Using `!` in the type/scope

```
feat!: send an email to the customer when a product is shipped
feat(api)!: send an email to the customer when a product is shipped
```

### 2. Using BREAKING CHANGE footer

```
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

### 3. Both methods

```
chore!: drop support for Node 6

BREAKING CHANGE: use JavaScript features not available in Node 6.
```

## Examples

### Simple feature

```
feat: add user authentication
```

### Feature with scope

```
feat(auth): add OAuth2 support
```

### Bug fix with body

```
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.
```

### Breaking change

```
feat!: migrate to new API client

BREAKING CHANGE: The API client interface has changed. All methods now
return Promises instead of using callbacks.
```

### Documentation update

```
docs: correct spelling of CHANGELOG
```

### Multi-paragraph body with footers

```
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.

Reviewed-by: Z
Refs: #123
```

## Guidelines

1. **Always use a type** - Every commit must start with a type followed by a colon and space
2. **Use imperative mood** - Write as if completing the sentence "If applied, this commit will..."
3. **Be specific** - The description should clearly communicate what changed
4. **Keep it focused** - One logical change per commit
5. **Use scopes when helpful** - Scopes help categorize changes within a codebase
6. **Document breaking changes** - Always indicate breaking changes clearly

## Semantic Versioning Correlation

- **`fix:`** → PATCH version bump (1.0.0 → 1.0.1)
- **`feat:`** → MINOR version bump (1.0.0 → 1.1.0)
- **BREAKING CHANGE** → MAJOR version bump (1.0.0 → 2.0.0)

## When to Use

Use this format for:
- All git commits
- Commit message generation
- Pull request merge commits
- When the user asks about commit messages or git commits

## Common Mistakes to Avoid

❌ `Added new feature` (past tense, capitalized)
✅ `feat: add new feature` (imperative, lowercase)

❌ `fix: bug` (too vague)
✅ `fix: resolve null pointer exception in user service`

❌ `feat: add feature` (redundant)
✅ `feat: add user profile page`

❌ `feat: Added OAuth support.` (past tense, period)
✅ `feat: add OAuth support`
