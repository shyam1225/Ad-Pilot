import os
from dotenv import load_dotenv
from openai import OpenAI
from app.schemas.campaign import CampaignStrategy

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY is missing from .env")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

def generate_response(prompt: str):

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "system",
                "content": """
                You are an expert digital marketing strategist.

                Generate practical advertising campaign strategies.

                Return ONLY valid JSON with these fields:
                - summary: string
                - recommended_platforms: list of strings
                - budget_allocation: list of objects containing
                  platform, amount, and reason
                - ad_copy: list of strings

                Do not include Markdown code fences.
                """
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"}
    )

    return response.choices[0].message.content
