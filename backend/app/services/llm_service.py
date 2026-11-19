
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.schemas.campaign import CampaignStrategy

load_dotenv()



client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_response(prompt: str):

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="""
            You are an expert digital marketing strategist.

            Generate practical advertising campaign strategies.
            Follow the requested output structure.
            Keep the total budget allocation equal to
            the user's specified budget.
            """,
            response_mime_type="application/json",
            response_schema=CampaignStrategy
        )
    )

    if response.parsed is None:
        raise ValueError("Gemini did not return a structured response")

    return response.parsed
