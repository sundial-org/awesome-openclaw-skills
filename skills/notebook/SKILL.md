---
name: Notebook
description: Local-first personal knowledge base for tracking ideas, projects, tasks, habits, and any object type you define. YAML-based with no cloud lock-in.
---

# Notebook Skill Object Based Personal Knowledge Base

Purpose: Track any object type you define such as ideas, projects, tasks, habits, books, and people.

Location: {WORKSPACE}/skills/notebook/

## Agent Onboarding Protocol

Guide the user through setup when no object types exist.

### Step 1 Suggest a First Type

```
It looks like you have not defined any object types yet.
Notebook works best when you define the types of things you want to track.

What would you like to start with?

1. Ideas for capturing thoughts and features
2. Projects for long term work with goals
3. Tasks for actionable items with due dates
4. Something custom tell me what you want to track
```

### Step 2 Define the Type Together

If they choose a preset:
```
Great. Let us set up [type].

I will create it with useful fields. You can add or remove them later.

For [type], what fields do you want?
- title (text, required)
- status (select)
- priority (select)
- tags (text)
- notes (longtext)
- [custom fields]

What fields should [type] have?
```

If they want custom:
```
Tell me what you want to track and what details matter.

Example: I want to track books I read. I need title, author, status, rating, and notes.

I will translate that into a type definition.
```

### Step 3 Create the First Object

```
Now let us add your first [type].

What do you want to track as your first [type]?

Example: The Andromeda Strain for books or Home automation for projects
```

### Step 4 Show the Workflow

```
Perfect. You now have:
- Type: [typename] with [N] fields
- 1 [typename] object: [title]

What would you like to do next?

- notebook list [typename] to see all items
- notebook expand [typename] [title] to add details
- notebook add [typename] to add another
- notebook type-add [typename] to add more fields later
```

### Step 5 Offer Expansion

```
Would you like to deepen this [typename] with some questions?
Say expand and I will ask questions to add depth.
```

## Quick Reference

### Defining Types

```
notebook type-add typename field1:text field2:select(a|b|c) field3:number
```

Field types:
- text for short strings
- longtext for multi line notes
- select(a|b|c) for one option from a list
- number for numeric values
- date for dates
- list for an array of strings

### Working with Objects

```
notebook add typename "Title" [-t tag1,tag2 -p priority]
notebook list typename
notebook get typename title
notebook expand typename title
notebook edit typename "title" field:value
notebook link type1:title1 type2:title2
notebook delete typename title
notebook find "query"
notebook stats
```

## Example Workflow

```
# 1. Define a type
notebook type-add idea title:text status:select(raw|expanded|archived) priority:select(high|medium|low) tags:text notes:longtext

# 2. Add your first idea
notebook add idea "Voice capture while driving" -t voice,automation -p high

# 3. Deepen it
notebook expand idea "voice capture"

# 4. Link to other objects
notebook add project "Home automation" -t household
notebook link idea:"voice capture" project:"home automation"

# 5. Update as you work
notebook edit idea "voice capture" status:expanded
```

## Data Location

```
/data/notebook/
├── objects/
├── types.yaml
└── index.json
```

## Design Principles

- User defined: You define the types that matter.
- Local first: Uses YAML files with no cloud or vendor lock in.
- Linkable: Objects can reference each other.
- Extensible: Add types and fields as needed.
- Expandable: Use intelligent questioning to deepen thinking.