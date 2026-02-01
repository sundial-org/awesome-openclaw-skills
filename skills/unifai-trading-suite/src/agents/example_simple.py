"""Minimal UnifAI agent example - single query."""

import asyncio
import os
from dotenv import load_dotenv
import unifai
import litellm

load_dotenv()

DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemini/gemini-3-flash-preview")


async def run_single_query(query: str) -> str:
    """Run a single query through UnifAI with Gemini."""
    tools = unifai.Tools(api_key=os.getenv("UNIFAI_AGENT_API_KEY"))

    # Get dynamic tools from UnifAI network
    available_tools = await tools.get_tools(dynamic_tools=True)

    # Call Gemini with the tools
    response = await litellm.acompletion(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": query}],
        tools=available_tools if available_tools else None,
        temperature=1.0,  # Gemini 3 requires temp=1.0 to avoid looping
    )

    message = response.choices[0].message

    # If the model wants to use tools, execute them
    if message.tool_calls:
        results = await tools.call_tools(message.tool_calls)
        print(f"Tool calls executed: {len(results)}")
        for i, result in enumerate(results):
            print(f"  [{i+1}] {result}")

        # Get final response with tool results
        messages = [
            {"role": "user", "content": query},
            message.model_dump(),
        ]
        for tool_call, result in zip(message.tool_calls, results):
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            })

        final = await litellm.acompletion(
            model=DEFAULT_MODEL,
            messages=messages,
            temperature=1.0,  # Gemini 3 requires temp=1.0
        )
        return final.choices[0].message.content or ""

    return message.content or ""


async def main():
    """Run example queries."""
    queries = [
        "What tools are available for cryptocurrency data?",
        "What is the current price of Bitcoin?",
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print("-" * 60)
        try:
            result = await run_single_query(query)
            print(f"Response: {result}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
