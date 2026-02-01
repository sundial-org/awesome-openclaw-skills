# Context Compressor Skill

Automated context management for long-running Clawdbot sessions. Detects when context limits approach, compresses old conversation history, and seamlessly transfers to a fresh session.

## When to Use

- Long coding sessions with extensive context accumulation
- Projects with many iterations and refinements
- When noticing Claude repeating itself or losing track of details
- Proactively before hitting hard context limits
- During heartbeats or idle moments when user isn't actively waiting

## How It Works

1. **Monitoring**: Continuously tracks context usage via session metadata
2. **Compression**: When threshold reached (configurable, default 80%), summarizes old messages
3. **Preservation**: Extracts key decisions, code changes, file states, and action items
4. **Handoff**: Initiates new session with compressed context as foundation
5. **Continuity**: User experiences seamless transition with all important context preserved

## Key Features

- **Smart Summarization**: Preserves decisions, code, file states, not just raw text
- **Configurable Thresholds**: Set when compression triggers (70-90% of context limit)
- **Background Operation**: Works during heartbeats or low-activity periods
- **Selective Retention**: Keeps important files, decisions, TODOs; compresses chaff
- **Session State Transfer**: New session inherits all critical context automatically

## Core Concepts

### Context Degradation Patterns

As sessions grow long, watch for these signs:
- Repetitive responses ("As I mentioned earlier...")
- Missing references to earlier decisions
- Forgetting file modifications
- Asking to repeat information
- General coherence degradation

### Compression Strategy

1. **Extract Core Intelligence**:
   - All decisions made and their rationale
   - File paths and their current state
   - Pending tasks and their status
   - Important code snippets or configurations
   - User preferences and patterns

2. **Condense History**:
   - Remove filler, backtracking, dead ends
   - Keep only high-signal turns
   - Merge related iterations into summaries
   - Preserve critical code snippets inline

3. **Format for Efficiency**:
   - Use compact representations
   - Reference files rather than dump contents
   - List decisions as bullet points
   - Include only relevant code context

## Usage

### Automatic Mode (Recommended)

The skill runs automatically during heartbeats and idle periods. Configure threshold:

```bash
# Set compression to trigger at 75% context usage
context-compressor set-threshold 75

# Check current status
context-compressor status
```

### Manual Trigger

```bash
# Force compression and session reset
context-compressor compress --force
```

### Configuration

```bash
# View all settings
context-compressor config

# Adjust summarization depth
context-compressor set-depth brief|detailed|comprehensive

# Set quiet hours (compression won't run)
context-compressor set-quiet-hours 23:00-07:00
```

## Output

When compression occurs, the skill produces:

1. **Summary File**: `memory/compressed-{session-id}.md`
   - Executive summary of session
   - Key decisions made
   - Files modified and their states
   - Pending tasks
   - Code snippets worth preserving

2. **Session Handoff**: Automatic new session with:
   - User context (USER.md)
   - Project memory (MEMORY.md)
   - Compressed session summary
   - Current working state

## Best Practices

1. **Regular Compression**: Don't wait for limits. Compress proactively every few hours
2. **Preserve Code**: Always keep actual code snippets, not just references
3. **Track Decisions**: Explicitly note WHY decisions were made, not just WHAT
4. **Keep TODOs**: Mark incomplete work clearly for continuity
5. **Reference Files**: Point to files rather than embedding full contents

## Integration Points

- **Heartbeats**: Runs compression checks during heartbeat cycles
- **Memory System**: Writes compressed summaries to memory files
- **Session Management**: Coordinates with session spawn for handoff
- **File Tracking**: References current file states accurately

## Technical Details

### Compression Algorithm

1. Parse session transcript into atomic turns
2. Score each turn for importance (decisions = high, chat = low)
3. Keep top N% of turns by importance score
4. Summarize remaining turns into executive summary
5. Extract and preserve code blocks separately
6. Generate session transfer package

### Thresholds

- **Conservative (70%)**: Trigger early, preserve more context
- **Balanced (80%)**: Default, good for most workflows  
- **Aggressive (90%)**: Push limits, maximum session length
- **Manual Only**: Disable auto-trigger, compress on demand

### File References

The compressor tracks:
- Modified files and their paths
- Configuration changes
- New files created
- Deleted files
- Directory structure changes

## Troubleshooting

### Compression Too Frequent

```bash
# Increase threshold
context-compressor set-threshold 85
```

### Context Lost After Handoff

Check that:
1. Compressed summary was generated (`memory/compressed-*.md`)
2. New session loaded memory files
3. Critical files weren't in the "chaff" that got dropped

### Performance Impact

Compression runs in background and should complete in <30s for typical sessions. If slower:
- Reduce summarization depth
- Increase threshold to compress less frequently
- Exclude large files from compression scope

## Examples

### Typical Workflow

```
User: Working on notes app sidebar
[Session runs 2 hours, many iterations]

Heartbeat triggers → Context at 78% → Auto-compress → New session
User: (no interruption, seamless continuation)
New session has: executive summary, key decisions, file states, TODOs
```

### Manual Recovery

```
User notices Claude repeating itself
User: "context-compressor compress --force"
Compressor summarizes → New session starts → User continues seamlessly
```

## Related Skills

- **memory-system**: Underlying memory infrastructure
- **self-improving-agent**: Learns from session patterns
- **sessions-spawn**: Handles new session creation

## See Also

- [Context Engineering Skills Collection](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering)
- Research on "lost-in-the-middle" phenomenon in LLM context windows
