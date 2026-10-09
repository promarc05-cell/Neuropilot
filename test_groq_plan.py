
import os
from dotenv import load_dotenv
from groq import Groq


def main():
    load_dotenv()

    print("=" * 50)
    print("NEUROPILOT - GROQ API TEST")
    print("=" * 50)

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("ERROR: GROQ_API_KEY is missing.")
        return

    assignment = input("\nEnter your assignment:\n> ").strip()

    if not assignment:
        print("ERROR: Assignment cannot be empty.")
        return

    try:
        client = Groq(api_key=api_key)

        print("\nSending request to Groq...")

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are NeuroPilot, an assistant that breaks "
                        "student assignments into practical, manageable "
                        "tasks. Respond in plain text. Do not return JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Understand this assignment and suggest 3 to 6 "
                        "specific tasks with estimated durations.\n\n"
                        f"Assignment: {assignment}"
                    ),
                },
            ],
            temperature=0,
            max_completion_tokens=1500,
        )

        result = response.choices[0].message.content

        if result:
            print("\nSUCCESS: Groq API responded!")
            print("\nAI-generated task suggestions:\n")
            print(result)
        else:
            print("Groq returned an empty response.")
            print("Finish reason:", response.choices[0].finish_reason)

    except Exception as error:
        print("\nGroq API request failed.")
        print("Error type:", type(error).__name__)
        print("Details:", str(error))


if __name__ == "__main__":
    main()
