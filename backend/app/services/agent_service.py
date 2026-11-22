import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from app.services.tools import calculate_budget
import json
from langchain_core.messages import HumanMessage, ToolMessage
load_dotenv()

llm = ChatOpenAI(
    model="openrouter/free",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0
)

