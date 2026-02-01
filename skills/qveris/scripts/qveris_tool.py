#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx",
# ]
# ///
"""
QVeris Tool Search & Execution CLI

Search for tools by capability and execute them via QVeris API.

Usage:
    uv run qveris_tool.py search "weather forecast"
    uv run qveris_tool.py execute <tool_id> --search-id <id> --params '{"city": "London"}'
"""

import argparse
import asyncio
import json
import os
import sys

import httpx

BASE_URL = "https://qveris.ai/api/v1"


def get_api_key() -> str:
    """Get QVeris API key from environment."""
    key = os.environ.get("QVERIS_API_KEY")
    if not key:
        print("Error: QVERIS_API_KEY environment variable not set", file=sys.stderr)
        print("Get your API key at https://qveris.ai", file=sys.stderr)
        sys.exit(1)
    return key


async def search_tools(query: str, limit: int = 5) -> dict:
    """Search for tools matching a capability description."""
    api_key = get_api_key()

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{BASE_URL}/search",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"query": query, "limit": limit},
        )
        response.raise_for_status()
        return response.json()


async def execute_tool(
    tool_id: str,
    search_id: str,
    parameters: dict,
    max_response_size: int = 20480,
) -> dict:
    """Execute a specific tool with parameters."""
    api_key = get_api_key()

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{BASE_URL}/tools/execute",
            params={"tool_id": tool_id},
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "search_id": search_id,
                "parameters": parameters,
                "max_response_size": max_response_size,
            },
        )
        response.raise_for_status()
        return response.json()


def display_search_results(result: dict) -> None:
    """Display search results in a formatted way."""
    search_id = result.get("search_id", "N/A")
    tools = result.get("results", [])
    total = result.get("total", len(tools))

    print(f"\nSearch ID: {search_id}")
    print(f"Found {total} tools\n")

    if not tools:
        print("No tools found.")
        return

    for i, tool in enumerate(tools, 1):
        tool_id = tool.get("tool_id", "N/A")
        name = tool.get("name", "N/A")
        desc = tool.get("description", "N/A")

        # Stats
        stats = tool.get("stats", {})
        success_rate = stats.get("success_rate", "N/A")
        avg_time = stats.get("avg_execution_time_ms", "N/A")

        if isinstance(success_rate, (int, float)):
            success_rate = f"{success_rate:.0%}"
        if isinstance(avg_time, (int, float)):
            avg_time = f"{avg_time:.1f}ms"

        print(f"[{i}] {name}")
        print(f"    ID: {tool_id}")
        print(f"    {desc[:100]}{'...' if len(desc) > 100 else ''}")
        print(f"    Success: {success_rate} | Avg Time: {avg_time}")

        # Show params
        params = tool.get("params", [])
        if params:
            required = [p["name"] for p in params if p.get("required")]
            optional = [p["name"] for p in params if not p.get("required")]
            if required:
                print(f"    Required: {', '.join(required)}")
            if optional:
                print(f"    Optional: {', '.join(optional[:5])}{'...' if len(optional) > 5 else ''}")

        # Show example
        examples = tool.get("examples", {})
        sample = examples.get("sample_parameters")
        if sample:
            print(f"    Example: {json.dumps(sample)}")

        print()


def display_execution_result(result: dict) -> None:
    """Display tool execution result."""
    success = result.get("success", False)
    exec_time = result.get("elapsed_time_ms", "N/A")
    cost = result.get("cost", 0)

    status = "Success" if success else "Failed"
    print(f"\n{status}")
    print(f"Time: {exec_time}ms | Cost: {cost}")

    if not success:
        error = result.get("error_message", "Unknown error")
        print(f"Error: {error}")

    data = result.get("result", {})
    if data:
        print("\nResult:")
        print(json.dumps(data, indent=2, ensure_ascii=False))


async def main():
    parser = argparse.ArgumentParser(
        description="QVeris Tool Search & Execution CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search "weather forecast API"
  %(prog)s execute openweathermap_current_weather --search-id abc123 --params '{"city": "London"}'
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for tools")
    search_parser.add_argument("query", help="Capability description to search for")
    search_parser.add_argument("--limit", type=int, default=5, help="Max results (default: 5)")
    search_parser.add_argument("--json", action="store_true", help="Output raw JSON")

    # Execute command
    exec_parser = subparsers.add_parser("execute", help="Execute a tool")
    exec_parser.add_argument("tool_id", help="Tool ID to execute")
    exec_parser.add_argument("--search-id", required=True, help="Search ID from previous search")
    exec_parser.add_argument("--params", default="{}", help="Tool parameters as JSON string")
    exec_parser.add_argument("--max-size", type=int, default=20480, help="Max response size")
    exec_parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    try:
        if args.command == "search":
            result = await search_tools(args.query, args.limit)
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                display_search_results(result)

        elif args.command == "execute":
            params = json.loads(args.params)
            result = await execute_tool(
                args.tool_id,
                args.search_id,
                params,
                args.max_size,
            )
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                display_execution_result(result)

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code}", file=sys.stderr)
        print(e.response.text, file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in --params: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
