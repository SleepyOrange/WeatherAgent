#!/usr/bin/env python3
"""Weather Agent CLI - A conversational weather assistant powered by Claude."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def check_api_keys():
    """Verify required API keys are set."""
    missing = []
    if not os.getenv("ANTHROPIC_API_KEY"):
        missing.append("ANTHROPIC_API_KEY")
    if not os.getenv("OPENWEATHERMAP_API_KEY"):
        missing.append("OPENWEATHERMAP_API_KEY")

    if missing:
        print("Missing required API keys:")
        for key in missing:
            print(f"  - {key}")
        print("\nPlease create a .env file with your API keys.")
        print("See .env.example for reference.")
        sys.exit(1)


def main():
    """Run the weather agent CLI."""
    check_api_keys()

    from agent import WeatherAgent

    print("=" * 50)
    print("  Weather Agent - Powered by Claude")
    print("=" * 50)
    print("\nAsk me anything about the weather!")
    print("Examples:")
    print("  - What's the weather in London?")
    print("  - Will it rain in Tokyo tomorrow?")
    print("  - Give me a 5-day forecast for New York")
    print("\nType 'quit' or 'exit' to end the session.")
    print("Type 'clear' to start a new conversation.")
    print("-" * 50)

    agent = WeatherAgent()

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except EOFError:
            print("\n\nGoodbye! Stay weather-aware!")
            break

        try:
            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print("\nGoodbye! Stay weather-aware!")
                break

            if user_input.lower() == "clear":
                agent.reset()
                print("\nConversation cleared. Starting fresh!")
                continue

            print("\nWeather Agent: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)

        except KeyboardInterrupt:
            print("\n\nGoodbye! Stay weather-aware!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.")


if __name__ == "__main__":
    main()
