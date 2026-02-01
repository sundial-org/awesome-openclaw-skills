# swelist --- Agent & Automation Usage Guide

This document defines the operational capabilities, invocation contract,
and usage semantics of the `swelist` CLI tool for AI agents, schedulers,
and automation systems.

------------------------------------------------------------------------

## Tool Identity

-   **Name:** swelist
-   **Type:** Command-Line Interface (CLI)
-   **Language:** Python
-   **Distribution:** PyPI
-   **Execution Model:** Stateless, read-only

------------------------------------------------------------------------

## Purpose

`swelist` retrieves recently added technology internship and
new‑graduate job postings from curated public GitHub repositories and
renders them in a predictable, text-based format.

It is optimized for: - Automation pipelines - Periodic polling agents -
Human-in-the-loop job search workflows

------------------------------------------------------------------------

## Data Sources

-   SimplifyJobs / Summer2025-Internships
-   SimplifyJobs / New-Grad-Positions

Data is fetched live at runtime.

------------------------------------------------------------------------

## Installation

``` bash
pip install swelist
```

------------------------------------------------------------------------

## Invocation Contract

``` bash
swelist [--role ROLE] [--timeframe TIMEFRAME]
```

The tool accepts only CLI flags. No stdin is consumed.

------------------------------------------------------------------------

## Parameters

### --role

Controls which category of jobs to retrieve.

  Value        Meaning
  ------------ ----------------------------
  internship   Internship roles (default)
  newgrad      New‑graduate roles

Example:

``` bash
swelist --role newgrad
```

------------------------------------------------------------------------

### --timeframe

Controls recency filtering.

  Value       Time Window
  ----------- ---------------
  lastday     Last 24 hours
  lastweek    Last 7 days
  lastmonth   Last 30 days

Example:

``` bash
swelist --timeframe lastweek
```

------------------------------------------------------------------------

## Output Contract

-   Output is written to **STDOUT**
-   Format is **human- and agent-readable plain text**
-   No JSON or structured serialization

### Job Posting Fields

Each job entry contains:

-   Company (string)
-   Title (string)
-   Location (string)
-   Link (URL)

Example:

    Company: Example Corp
    Title: Software Engineer Intern
    Location: Remote
    Link: https://example.com/apply

------------------------------------------------------------------------

## Execution Guarantees

-   No side effects
-   No persistent storage
-   Safe for repeated execution
-   Deterministic given identical upstream data
-   No authentication required

------------------------------------------------------------------------

## Error Behavior

-   Network issues may raise runtime errors or result in empty output
-   Invalid flags produce CLI usage errors
-   Zero matching jobs produces valid empty result output

------------------------------------------------------------------------

## Environment Requirements

-   Python 3.8+
-   Internet access
-   Supported on macOS, Linux, Windows

------------------------------------------------------------------------

## Agent-Oriented Use Cases

-   Daily polling for new internship postings
-   Weekly new‑grad job aggregation
-   Feeding results into ranking, scoring, or alerting agents
-   Execution via cron, CI pipelines, or autonomous agents

------------------------------------------------------------------------

## Known Limitations

-   No built‑in alerting
-   No local caching
-   No deduplication beyond source data
-   No JSON output format

------------------------------------------------------------------------

## Safety & Compliance

-   Uses only public data
-   No user tracking
-   No credential usage
-   No scraping of private systems

------------------------------------------------------------------------

## Versioning

Behavior may evolve with upstream data sources. CLI flags are considered
stable within a major version.

------------------------------------------------------------------------

End of document.
