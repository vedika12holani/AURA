
import os
from dotenv import load_dotenv
from aura_core.ai_core import AuraAICore

def main():
    # Load the environment variables from the .env file
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("🔴 Error: GOOGLE_API_KEY not found. Please create a .env file.")
        return

    # Initialize our AI core
    ai_core = AuraAICore(api_key=api_key)
    print("✨ Aura AI Core Initialized ✨")
    print("-" * 30)

    # --- 1. Test the Direct Command Generation ---
    print("\n🧪 Testing Direct Command Generation...")
    ai_core.get_direct_command()  # now takes input inside the function

    print("-" * 30)
    print("\n🧪 Starting Socratic Tutor (type 'exit' to end)")

    ai_core.reset_conversation()
    initial_prompt = input("   🗣️ Enter your initial request: ")

    # Get the AI's first question
    ai_question = ai_core.start_socratic_dialogue(initial_prompt)

    # Continue the interactive Socratic dialogue
    while True:
        user_response = input("\n   ➡️ Your Response (Type 'exit' to quit the mode): ")
        if user_response.lower() == 'exit':
            print("👋 Ending Socratic dialogue.")
            break

        ai_question = ai_core.start_socratic_dialogue(user_response)


if __name__ == "__main__":
    main()
