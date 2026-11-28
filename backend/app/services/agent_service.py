import os
from dotenv import load_dotenv
from app.core.llm import get_chat_llm
from app.services.tools import calculate_budget

load_dotenv()

llm = get_chat_llm(temperature=0)
