# Conversation Patterns for Process Knowledge

This document describes patterns for recognizing, tracking, and learning from
the structure of work — not *what* we know, but *how work proceeds*.

These patterns are grounded in the Language-Action Perspective (Winograd & Flores),
which treats work as networks of commitments made through language.

---

## Decision Matrix: What Kind of Conversation Is This?

| Signal | Conversation Type | Your Stance | Don't Do This |
|--------|-------------------|-------------|---------------|
| "Can you...", "Please...", "I need..." | **Action** | Clarify → Promise → Deliver | Promise before understanding |
| "What if...", "Imagine...", "Could we..." | **Possibility** | Explore, generate options, hold lightly | Commit prematurely |
| "What is...", "How does...", "Why..." | **Clarification** | Explain until understanding lands | Over-answer; assume you know the real question |
| "I'm trying to understand...", "Context is..." | **Orientation** | Listen, reflect back, surface assumptions | Jump to solutions |
| "Here's what I found...", "Status update..." | **Report** | Acknowledge, ask what's needed next | Assume it's a request |

**Transition signals** (conversation type is shifting):
- Possibility → Action: "Let's do X" / "I want to go with..."
- Clarification → Action: "Ok, so please..." / "Now that I understand..."
- Orientation → Clarification: "So what does X mean?" / "Help me understand..."

**When uncertain:** Ask. "Are you exploring options, or would you like me to do something?"

---

## Core Insight

Work is not information processing. Work is **commitment management**.

When an agent assists with a task, it participates in a conversation with structure:
- Requests create openings
- Promises create obligations  
- Completion is declared, not merely achieved
- Satisfaction closes the loop

Understanding *where we are* in this structure is as important as understanding
*what we know* about the subject matter.

---

## The Basic Conversation for Action

```
     Customer                          Performer
         │                                 │
         │──── 1. Request ────────────────→│
         │                                 │
         │←─── 2. Promise (or Counter) ────│
         │                                 │
         │          [ work happens ]       │
         │                                 │
         │←─── 3. Declare Complete ────────│
         │                                 │
         │──── 4. Declare Satisfied ──────→│
         │                                 │
```

At any point: Withdraw, Decline, Renegotiate.

**For agents:** Recognizing this structure helps answer:
- "What has been asked of me?"
- "What have I committed to?"
- "What does 'done' look like?"
- "Who needs to be satisfied?"

---

## Conversation Types

### Request for Action
Someone asks for something to be done.

**Recognize by:** Imperative language, "can you", "please", "I need"

**Track:**
- What specifically was requested?
- Any conditions or constraints?
- Implicit quality criteria?
- Who is the customer (who declares satisfaction)?

**Completion:** Customer declares satisfaction, not performer declares done.

### Request for Information  
Someone asks to know something.

**Recognize by:** Questions, "what is", "how does", "why"

**Track:**
- What gap in understanding prompted this?
- What level of detail is appropriate?
- What would make this answer useful?

**Completion:** Questioner indicates understanding (often implicit).

### Offer
Someone proposes to do something.

**Recognize by:** "I could", "would you like me to", "I suggest"

**Track:**
- What conditions on acceptance?
- What's the scope of the offer?

**Completion:** Offer accepted → becomes promise. Offer declined → closed.

### Report / Declaration
Someone asserts a state of affairs.

**Recognize by:** Statements of fact, status updates, "I found that"

**Track:**
- What changed as a result of this declaration?
- Who needs to know?

**Completion:** Acknowledgment (may trigger new conversations).

---

## Conversations for Possibility

Possibility conversations explore "what could be" — no commitment yet.

**Recognize by:** "What if", "imagine", "we could", "brainstorm", "options"

**Your stance:**
- Generate, don't filter prematurely
- Hold ideas lightly — nothing is promised
- Expand the space before narrowing
- Name options without advocating

**Track:**
- Options generated
- Constraints surfaced
- Energy/interest signals ("that's interesting" vs "hmm")

**Completion:** Not satisfaction — rather, either:
- Transition to Action ("let's do X")
- Explicit close ("good to know our options")
- Energy dissipates naturally

**Critical:** Don't promise during possibility. "I could do X" is an option, not a commitment. The transition to action must be explicit.

```python
# Indexing possibility exploration
mem.remember(
    content="Explored three auth options: OAuth2, API keys, magic links. "
            "User showed interest in magic links for UX simplicity. No decision yet.",
    source_tags={
        "type": "possibility",
        "topic": "authentication",
        "options": "oauth2,api_keys,magic_links",
        "status": "open"
    }
)
```

---

## Breakdowns: Where Learning Happens

A **breakdown** occurs when the normal flow is interrupted:
- Expected response doesn't come
- Declared completion isn't satisfactory
- Preconditions weren't met
- Ambiguity surfaces mid-work

**Breakdowns are valuable.** They reveal assumptions that were invisible.

**Pattern for breakdown learning:**
```
1. Notice: "This isn't going as expected"
2. Articulate: "The assumption was X, but actually Y"
3. Repair: Complete the immediate conversation
4. Record: Capture the learning for future conversations of this type
```

When indexing a breakdown:
```python
mem.remember(
    content="Assumption: user wanted full rewrite. Actually: wanted minimal patch.",
    source_tags={
        "type": "breakdown",
        "conversation_type": "code_change_request", 
        "learning": "Ask about scope before starting large changes"
    }
)
```

---

## Nested and Linked Conversations

Real work involves conversations within conversations:

```
User requests feature
  └─ Agent promises feature
       └─ Agent requests clarification (sub-conversation)
       │    └─ User provides clarification
       │    └─ Agent acknowledges (closes sub-conversation)
       └─ Agent declares complete
  └─ User requests revision (linked follow-on)
       └─ ...
```

**Track parent/child relationships** to understand scope:
- Completing a sub-conversation doesn't complete the parent
- Breakdowns in child conversations may propagate up
- Context flows down (child inherits parent context)

---

## Recurrent Patterns by Domain

### Software Development

| Pattern | Structure | Completion Condition |
|---------|-----------|---------------------|
| Bug report | Request → Diagnosis → Fix → Verify | User confirms fix works |
| Feature request | Request → Clarify → Implement → Review → Accept | Stakeholder accepts |
| Code review | Offer(changes) → Review → Request(revisions) → Update → Approve | Reviewer approves |
| Refactor | Offer → Scope agreement → Execute → Verify behavior preserved | Tests pass, reviewer approves |

### Research / Analysis

| Pattern | Structure | Completion Condition |
|---------|-----------|---------------------|
| Question | Request(info) → Search → Synthesize → Present | Questioner satisfied |
| Hypothesis test | Declare(hypothesis) → Design test → Execute → Report | Evidence evaluated |
| Literature review | Request → Gather → Synthesize → Summarize | Comprehensive & relevant |

### Planning / Coordination

| Pattern | Structure | Completion Condition |
|---------|-----------|---------------------|
| Task breakdown | Request(outcome) → Decompose → Commit to parts → Track → Integrate | Outcome achieved |
| Decision | Present options → Evaluate → Declare choice | Commitment to proceed |
| Handoff | Declare(status) → Transfer commitments → Acknowledge | Receiving agent accepts |

---

## Agent Handoff as Commitment Transfer

When one agent hands off to another:

```python
# Outgoing agent records state
mem.set_context(
    summary="User requested OAuth2 implementation. I promised and partially delivered. "
            "Token acquisition works. Refresh flow incomplete. User awaiting completion.",
    active_items=["file:///src/oauth.py", "file:///docs/oauth-spec.md"],
    topics=["authentication", "oauth2"],
    metadata={
        "open_commitments": [
            {"type": "promise", "what": "working refresh flow", "to": "user"}
        ],
        "conversation_state": "performer_working",
        "completion_criteria": "refresh tokens automatically when expired"
    }
)
```

Incoming agent reads this and knows:
- There's an open promise to the user
- What "done" looks like
- Where to pick up

---

## Learning New Patterns

Agents can recognize and record new conversation patterns:

```python
mem.remember(
    content="""
    Pattern: Incremental Specification
    
    Observed in: Feature discussions where requirements emerge through dialogue
    
    Structure:
    1. User states vague goal
    2. Agent proposes concrete interpretation
    3. User corrects/refines
    4. Repeat until shared understanding
    5. Then: standard request-promise-complete
    
    Key insight: Don't promise until step 5. Before that, you're in 
    "conversation for clarification", not "conversation for action".
    
    Breakdown risk: Promising too early leads to rework.
    """,
    source_tags={
        "type": "conversation_pattern",
        "domain": "general",
        "learned_from": "session:2026-01-30:abc123"
    }
)
```

---

## Using Patterns in Practice

**At task start:**
1. What kind of conversation is this?
2. What's my role (customer or performer)?
3. What does completion look like?
4. Have I seen breakdowns in this pattern before?

**Mid-task:**
1. Where are we in the conversation structure?
2. Have any sub-conversations opened?
3. Are there signs of breakdown?

**At task end:**
1. Was satisfaction declared (not just completion)?
2. Any learnings to record?
3. Open commitments to hand off?

---

## References

- Winograd, T. & Flores, F. (1986). *Understanding Computers and Cognition*
- Denning, P. & Medina-Mora, R. (1995). "Completing the Loops"
- Flores, F. et al. (1988). "Computer Systems and the Design of Organizational Interaction"
