import os
import sys
import subprocess
from mac_controller import MacController
from agent import Agent, acknowledge_safety_check_callback


def main():
    """Main entry point for the application."""
    # Parse command line arguments
    enable_speech = True
    verbose = False
    instruction = None

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--no-speech":
            enable_speech = False
            i += 1
        elif sys.argv[i] == "--verbose":
            verbose = True
            i += 1
        elif sys.argv[i] == "--help" or sys.argv[i] == "-h":
            print("Usage: python3 main.py [--no-speech] [--verbose] [instruction]")
            print("eg: `python3 main.py Open ChatGPT in Chrome`")
            print("Options:")
            print("  --no-speech    Disable speech announcements")
            print("  --verbose      Enable verbose (debug) mode")
            print("  --help, -h     Show this help message")
            return
        else:
            # Assume the rest is the instruction
            instruction = " ".join(sys.argv[i:])
            break

    # Require an instruction to be provided
    if not instruction:
        print(
            "Error: Please provide a task. Eg: `python3 main.py Open ChatGPT in Chrome`"
        )
        sys.exit(1)

    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set it with: export OPENAI_API_KEY='your-api-key'")
        return

    print(
        f"Starting OpenAI Computer Use on macOS. "
        f"Press Ctrl+C to stop.\n"
        f"Speech announcements: {'Enabled' if enable_speech else 'Disabled'}. "
        f"Verbose mode: {'Enabled' if verbose else 'Disabled'}\n"
        f'------ Task: "{instruction}" ------\n'
    )

    # Initialize the computer and agent
    with MacController(enable_speech=enable_speech) as computer:
        agent = Agent(
            computer=computer,
            model="computer-use-preview",
            acknowledge_safety_check_callback=acknowledge_safety_check_callback,
        )

        # Start with initial instruction
        items = [
            {"role": "user", "content": instruction},
        ]

        try:
            # Process the initial instruction with verbose as debug flag
            output_items = agent.run_full_turn(items, print_steps=True, debug=verbose)
            items += output_items

            # Enter a loop for continuous interaction
            while True:
                user_input = input("> ")
                items.append({"role": "user", "content": user_input})
                output_items = agent.run_full_turn(
                    items, print_steps=True, debug=verbose
                )
                items += output_items

        except KeyboardInterrupt:
            print("\nExiting...")
            if enable_speech:
                subprocess.run(["say", "Exiting..."], check=False)
        except Exception as e:
            print(f"An error occurred: {e}")
            if enable_speech:
                subprocess.run(["say", f"Error: {str(e)}"], check=False)


if __name__ == "__main__":
    main()
