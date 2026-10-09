
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is missing. Set it in PowerShell first."
    )

client = Groq(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": (
                    "Reply with exactly this sentence: "
                    "NeuroPilot Groq connection successful."
                ),
            }
        ],
        temperature=0,
        max_completion_tokens=50,
    )

    print("Groq API connection successful!")
    print("Model response:", response.choices[0].message.content)

except Exception as error:
    print("Groq API request failed.")
    print("Error type:", type(error).__name__)
    print("Details:", str(error))
