#!/usr/bin/env python3
"""
Pulse Editor Vibe Dev Flow API Example

This script demonstrates how to use the Vibe Dev Flow API to generate
a new Pulse App with real-time SSE streaming progress updates.

Usage:
    python generate_app.py

Requirements:
    pip install requests

Environment Variables:
    PULSE_EDITOR_API_KEY - Your Pulse Editor API key
"""

import os
import json
import requests
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class AgentTaskMessage:
    """Represents a message from the Vibe Dev Flow SSE stream."""
    message_id: str
    msg_type: str  # "creation" or "update"
    data_type: str = ""  # "text", "toolCall", "toolResult", "artifactOutput"
    result: str = ""
    error: str = ""
    is_final: bool = False


class MessageTracker:
    """Tracks and updates messages from the SSE stream."""
    
    def __init__(self):
        self.messages: dict[str, AgentTaskMessage] = {}
    
    def handle_message(self, data: dict) -> Optional[AgentTaskMessage]:
        """
        Handle an SSE message (creation or update).
        
        Returns the updated/created message.
        """
        msg_type = data.get("type")
        message_id = data.get("messageId")
        
        if msg_type == "creation":
            # New message
            msg = AgentTaskMessage(
                message_id=message_id,
                msg_type="creation",
                data_type=data.get("data", {}).get("type", ""),
                result=data.get("data", {}).get("result") or "",
                error=data.get("data", {}).get("error") or "",
                is_final=data.get("isFinal", False)
            )
            self.messages[message_id] = msg
            return msg
        
        elif msg_type == "update":
            # Update existing message with delta
            msg = self.messages.get(message_id)
            if msg:
                delta = data.get("delta", {})
                msg.result += delta.get("result") or ""
                msg.error += delta.get("error") or ""
                msg.is_final = data.get("isFinal", False)
                return msg
        
        return None
    
    def get_artifactOutput(self) -> Optional[dict]:
        """
        Find and parse the artifact output message.
        
        Returns parsed artifact data with publishedAppLink, appId, etc.
        """
        for msg in self.messages.values():
            if msg.data_type == "artifactOutput" and msg.is_final and msg.result:
                try:
                    return json.loads(msg.result)
                except json.JSONDecodeError:
                    pass
        return None


def generate_pulse_app(
    prompt: str,
    api_key: str,
    app_name: Optional[str] = None,
    app_id: Optional[str] = None,
    version: Optional[str] = None
) -> Optional[dict]:
    """
    Generate a Pulse App using the Vibe Dev Flow API.
    
    Args:
        prompt: The user prompt instructing the Vibe coding agent
        api_key: Pulse Editor API key
        app_name: Optional friendly display name for the app
        app_id: Optional ID of existing app to update
        version: Optional version to base the update on
    
    Returns:
        Dict with publishedAppLink, sourceCodeArchiveLink, appId, version
        or None if generation failed.
    """
    url = "https://pulse-editor.com/api/server-function/vibe_dev_flow/latest/generate-code/v2/generate"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {"prompt": prompt}
    
    # Add optional parameters if provided
    if app_name:
        payload["appName"] = app_name
    if app_id:
        payload["appId"] = app_id
    if version:
        payload["version"] = version
    
    print(f"🚀 Starting Vibe Dev Flow")
    if app_name:
        print(f"📱 App: {app_name}")
    print(f"📝 Prompt: {prompt}")
    print("-" * 50)
    
    tracker = MessageTracker()
    buffer = ""
    
    try:
        # Make streaming request
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            stream=True,
            timeout=300  # 5 minute timeout for long generations
        )
        
        # Check for errors
        if response.status_code == 401:
            print("❌ Error: Unauthorized. Check your API key.")
            return None
        elif response.status_code == 400:
            print(f"❌ Error: Bad request. {response.text}")
            return None
        elif response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            return None
        
        # Process SSE stream with proper buffering
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                buffer += chunk
                
                # SSE messages are separated by \n\n
                while "\n\n" in buffer:
                    part, buffer = buffer.split("\n\n", 1)
                    
                    if not part.startswith("data:"):
                        continue
                    
                    # Remove "data: " prefix
                    json_str = part.replace("data: ", "", 1).replace("data:", "", 1)
                    
                    try:
                        data = json.loads(json_str)
                        msg = tracker.handle_message(data)
                        if msg:
                            display_message(msg, data.get("type") == "creation")
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Parse error: {e}")
        
        print("-" * 50)
        
        # Get final artifact output
        artifact = tracker.get_artifactOutput()
        if artifact:
            print("✅ Generation complete!")
            if artifact.get("publishedAppLink"):
                print(f"🔗 Published: {artifact['publishedAppLink']}")
            if artifact.get("sourceCodeArchiveLink"):
                print(f"📦 Source: {artifact['sourceCodeArchiveLink']}")
            print(f"🆔 App ID: {artifact.get('appId')}")
            if artifact.get("version"):
                print(f"📌 Version: {artifact['version']}")
            return artifact
        else:
            print("⚠️ Generation completed but no artifact output found")
            return None
        
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Error: Connection failed")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def display_message(msg: AgentTaskMessage, is_new: bool) -> None:
    """Display a message based on its type."""
    
    if msg.data_type == "text":
        if is_new and msg.result:
            # Only show first part of new text messages
            preview = msg.result[:100] + "..." if len(msg.result) > 100 else msg.result
            print(f"💬 {preview}")
    
    elif msg.data_type == "toolCall":
        if is_new:
            print(f"🔧 Tool call started...")
    
    elif msg.data_type == "toolResult":
        if msg.is_final:
            status = "✅" if not msg.error else "❌"
            print(f"{status} Tool completed")
    
    elif msg.data_type == "artifactOutput":
        if is_new:
            print(f"📦 Building artifact...")
    
    if msg.error and msg.is_final:
        print(f"❌ Error: {msg.error}")


def main():
    # Get API key from environment variable
    api_key = os.environ.get("PULSE_EDITOR_API_KEY")
    
    if not api_key:
        print("❌ Error: PULSE_EDITOR_API_KEY environment variable not set")
        print("\nTo set it:")
        print("  Windows:  set PULSE_EDITOR_API_KEY=your_api_key_here")
        print("  Linux/Mac: export PULSE_EDITOR_API_KEY=your_api_key_here")
        print("\nGet your API key at: https://pulse-editor.com/home/settings/developer")
        return
    
    # Example: Create a new app
    result = generate_pulse_app(
        prompt="Create a simple todo app with the ability to add, complete, and delete tasks. Include a clean modern UI with dark mode support.",
        api_key=api_key,
        app_name="My Todo App"
    )
    
    if result:
        print(f"\n🎉 Success! Your app is ready.")
    
    # Example: Update an existing app (uncomment to use)
    # result = generate_pulse_app(
    #     prompt="Add a calendar view to display tasks by due date",
    #     api_key=api_key,
    #     app_name="My Todo App",
    #     app_id="my_app_x7k9q2",
    #     version="0.0.1"
    # )


if __name__ == "__main__":
    main()
