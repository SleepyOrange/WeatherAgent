"""Claude-powered weather agent with tool use."""

import os
import json
from anthropic import Anthropic
from weather_tools import WeatherAPI, WEATHER_TOOLS


class WeatherAgent:
    """Weather assistant powered by Claude with tool use."""

    SYSTEM_PROMPT = """You are a helpful weather assistant. You can help users with:
- Getting current weather conditions for any location
- Providing weather forecasts for the next few days
- Answering questions about weather (will it rain, should I bring an umbrella, etc.)

When users ask about weather, use the available tools to get accurate, real-time data.
Be conversational and helpful. If a user asks a vague question like "what's the weather",
ask them to specify a location.

Always provide weather information in a clear, easy-to-read format.
Include relevant details like temperature, conditions, and any weather advisories.
"""

    def __init__(self):
        self.client = Anthropic()
        self.weather_api = WeatherAPI()
        self.conversation_history = []

    def _process_tool_call(self, tool_name: str, tool_input: dict) -> str:
        """Execute a tool and return the result."""
        if tool_name == "get_current_weather":
            result = self.weather_api.get_current_weather(
                location=tool_input["location"],
                units=tool_input.get("units", "metric"),
            )
        elif tool_name == "get_forecast":
            result = self.weather_api.get_forecast(
                location=tool_input["location"],
                days=tool_input.get("days", 5),
                units=tool_input.get("units", "metric"),
            )
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return json.dumps(result, indent=2)

    def chat(self, user_message: str) -> str:
        """
        Send a message to the agent and get a response.

        Args:
            user_message: The user's input message

        Returns:
            The agent's response text
        """
        self.conversation_history.append({"role": "user", "content": user_message})

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=self.SYSTEM_PROMPT,
            tools=WEATHER_TOOLS,
            messages=self.conversation_history,
        )

        # Process tool calls in a loop until we get a final response
        while response.stop_reason == "tool_use":
            # Extract tool use blocks
            tool_use_block = next(
                block for block in response.content if block.type == "tool_use"
            )

            tool_name = tool_use_block.name
            tool_input = tool_use_block.input

            # Execute the tool
            try:
                tool_result = self._process_tool_call(tool_name, tool_input)
            except Exception as e:
                tool_result = json.dumps({"error": str(e)})

            # Add assistant's response and tool result to history
            self.conversation_history.append(
                {"role": "assistant", "content": response.content}
            )
            self.conversation_history.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_block.id,
                            "content": tool_result,
                        }
                    ],
                }
            )

            # Get the next response
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=self.SYSTEM_PROMPT,
                tools=WEATHER_TOOLS,
                messages=self.conversation_history,
            )

        # Extract the final text response
        final_response = ""
        for block in response.content:
            if hasattr(block, "text"):
                final_response += block.text

        # Add the final response to history
        self.conversation_history.append(
            {"role": "assistant", "content": response.content}
        )

        return final_response

    def reset(self):
        """Clear conversation history."""
        self.conversation_history = []
