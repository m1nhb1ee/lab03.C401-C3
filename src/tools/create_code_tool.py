from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_code_example(topic: str, complexity: str, include_wrong_example=True):
    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    if include_wrong_example:
        content = f"Create {topic} example at {complexity} level with wrong example and make comparison"
    else:
        content = f"Create {topic} example at {complexity} level"

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "user", "content": content}
        ],
    )

    return response.choices[0].message.content
