import os
from dotenv import load_dotenv
from app.core.llm import get_openai_client, get_api_key, DEFAULT_MODEL
from app.schemas.campaign import CampaignStrategy

load_dotenv()

api_key = get_api_key()
client = get_openai_client()


def generate_response(prompt: str):
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
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
