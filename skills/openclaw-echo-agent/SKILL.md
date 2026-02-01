# EchoAgent

EchoAgent is a minimal OpenClaw-compatible skill.

## What it does
- Accepts text input
- Uses a tool to process it
- Returns deterministic output

## Use case
This skill is intended as a reference example for building
and publishing OpenClaw agents.

## Entry point
agent.py

## Interoperability

This skill is designed to be used by other OpenClaw agents.

### Input
- text (string)

### Output
- result (string)

This agent can be safely chained inside multi-agent workflows.
