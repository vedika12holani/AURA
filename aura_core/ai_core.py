import google.generativeai as genai
from . import prompts

class AuraAICore:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 5,
            "max_output_tokens": 2048,
        }
        
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
        )
        
        self.conversation_history = []
        self.socratic_turn_count = 0
        self.partial_command = ""

    def _safe_response_text(self, response):
        # Fix: ensure we extract text properly from Gemini response
        try:
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    return ''.join([p.text for p in candidate.content.parts if hasattr(p, 'text')])
                elif hasattr(candidate, 'content'):
                    return str(candidate.content)
            elif isinstance(response, str):
                return response
        except Exception:
            pass
        return str(response)

    def get_direct_command(self):
        user_request = input("Enter your request: ")
        prompt = prompts.SIMPLE_COMMAND_PROMPT.format(user_request=user_request)
        response = self.model.generate_content(prompt)
        command = self._safe_response_text(response).replace('`', '')
        print("\nGenerated command:\n", command)
        return command

    def start_socratic_dialogue(self, user_request: str) -> str:
        if self.socratic_turn_count == 0:
            self.conversation_history = []
            self.partial_command = ""

        self.conversation_history.append(f"User: {user_request}")
        history_str = "\n".join(self.conversation_history)
        
        prompt = prompts.SOCRATIC_TUTOR_PROMPT.format(
            history=history_str,
            partial_command=self.partial_command
        )
        response = self.model.generate_content(prompt)
        ai_response = self._safe_response_text(response)
        self.conversation_history.append(f"Aura: {ai_response}")
        self.socratic_turn_count += 1

        print(f"\n🧩 Step {self.socratic_turn_count}: {ai_response}")

        if any(word in ai_response.lower() for word in ["confirm", "confirmation", "ready"]):
            user_confirmation = input("\n❓ Aura: Would you like me to generate the final command(s)? (yes/no): ").strip().lower()
            if user_confirmation in ["yes", "y"]:
                final_prompt = prompts.PARTIAL_COMMAND_PROMPT.format(history="\n".join(self.conversation_history))
                final_response = self.model.generate_content(final_prompt)
                final_command = self._safe_response_text(final_response).replace('`', '')
                print("\n✅ Final command(s):")
                print(final_command)
                print("\n📘 Explanation:")
                explain_prompt = prompts.EXPLAIN_COMMAND_PROMPT.format(command=final_command)
                explanation = self._safe_response_text(self.model.generate_content(explain_prompt))
                print(explanation)
                self.reset_conversation()
                return "Dialogue completed."
            else:
                print("\n🔁 Okay, let's clarify further.")

        partial_prompt = prompts.PARTIAL_COMMAND_PROMPT.format(history=history_str)
        partial_response = self.model.generate_content(partial_prompt)
        self.partial_command = self._safe_response_text(partial_response).replace('`', '')

        print("\n🔧 Partial command so far:")
        print(self.partial_command)
        print("\n📘 Explanation:")
        explain_prompt = prompts.EXPLAIN_COMMAND_PROMPT.format(command=self.partial_command)
        explanation = self._safe_response_text(self.model.generate_content(explain_prompt))
        print(explanation)

        if self.socratic_turn_count >= 6 or "final command" in ai_response.lower():
            print("\n🎯 Socratic dialogue complete.")
            print("✅ Final command suggestion:\n", self.partial_command)
            self.reset_conversation()

        return ai_response

    def reset_conversation(self):
        self.conversation_history = []
        self.socratic_turn_count = 0
        self.partial_command = ""
