"""Basic UnifAI agent example with Gemini integration."""

import asyncio
import os
from dotenv import load_dotenv
import unifai
import litellm

load_dotenv()

DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemini/gemini-3-flash-preview")


class TradingAgent:
    """A basic trading agent using UnifAI SDK and Gemini."""

    def __init__(
        self,
        agent_api_key: str | None = None,
        model: str | None = None,
    ):
        self.api_key = agent_api_key or os.getenv("UNIFAI_AGENT_API_KEY")
        if not self.api_key:
            raise ValueError("UNIFAI_AGENT_API_KEY is required")

        self.model = model or DEFAULT_MODEL
        self.tools = unifai.Tools(api_key=self.api_key)
        self.conversation_history: list[dict] = []

    async def get_available_tools(self, dynamic: bool = True) -> list:
        """Fetch available tools from UnifAI."""
        return await self.tools.get_tools(dynamic_tools=dynamic)

    async def chat(self, user_message: str) -> str:
        """Send a message and get a response, handling tool calls."""
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
        })

        available_tools = await self.get_available_tools()

        response = await litellm.acompletion(
            model=self.model,
            messages=self.conversation_history,
            tools=available_tools if available_tools else None,
            temperature=1.0,  # Gemini 3 requires temp=1.0 to avoid looping
        )

        assistant_message = response.choices[0].message

        # Handle tool calls if present
        if assistant_message.tool_calls:
            self.conversation_history.append(assistant_message.model_dump())

            # Execute tool calls via UnifAI
            tool_results = await self.tools.call_tools(assistant_message.tool_calls)

            # Add tool results to conversation
            for tool_call, result in zip(assistant_message.tool_calls, tool_results):
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })

            # Get final response after tool execution
            follow_up = await litellm.acompletion(
                model=self.model,
                messages=self.conversation_history,
                tools=available_tools if available_tools else None,
                temperature=1.0,  # Gemini 3 requires temp=1.0
            )
            final_message = follow_up.choices[0].message
            self.conversation_history.append(final_message.model_dump())
            return final_message.content or ""

        self.conversation_history.append(assistant_message.model_dump())
        return assistant_message.content or ""

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


async def main():
    """Example usage of the trading agent."""
    # Check for API key
    if not os.getenv("UNIFAI_AGENT_API_KEY"):
        print("Error: UNIFAI_AGENT_API_KEY not set")
        print("Get your API key from https://console.unifai.network")
        return

    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not set")
        print("Get your API key from https://aistudio.google.com")
        return

    agent = TradingAgent()

    print("Trading Agent initialized. Type 'quit' to exit.\n")

    # Show available tools
    tools = await agent.get_available_tools()
    print(f"Available tools: {len(tools)} dynamic tools loaded\n")

    # Interactive loop
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ("quit", "exit", "q"):
                break
            if not user_input:
                continue

            response = await agent.chat(user_input)
            print(f"\nAgent: {response}\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}\n")

    print("Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
