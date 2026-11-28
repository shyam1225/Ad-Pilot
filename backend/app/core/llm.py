import os
import json
import typing
from pathlib import Path
from typing import Type, TypeVar, Optional, Any, get_origin, get_args
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError

# Search for .env in current dir and backend root
backend_env = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=backend_env)
load_dotenv()

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")
DEFAULT_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")


def get_api_key() -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is missing from environment / .env")
    return api_key


def get_openai_client() -> OpenAI:
    """Returns a direct OpenAI client configured for OpenRouter."""
    return OpenAI(
        base_url=DEFAULT_BASE_URL,
        api_key=get_api_key()
    )


def get_chat_llm(temperature: float = 0.0, model: Optional[str] = None) -> ChatOpenAI:
    """Returns a LangChain ChatOpenAI client configured for OpenRouter."""
    return ChatOpenAI(
        model=model or DEFAULT_MODEL,
        api_key=get_api_key(),
        base_url=DEFAULT_BASE_URL,
        temperature=temperature
    )


def _build_field_example(field_name: str, field_info: Any) -> Any:
    annotation = field_info.annotation
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is list:
        sub_type = args[0] if args else str
        if hasattr(sub_type, "model_fields"):
            return [{k: _build_field_example(k, v) for k, v in sub_type.model_fields.items()}]
        return [f"<{field_name}_item>"]
    elif hasattr(annotation, "model_fields"):
        return {k: _build_field_example(k, v) for k, v in annotation.model_fields.items()}
    elif annotation is int or annotation is float:
        return 0
    elif annotation is bool:
        return True
    else:
        desc = field_info.description or f"<{field_name}>"
        return f"string: {desc}"


def build_json_template_example(schema: Type[BaseModel]) -> str:
    """
    Constructs an intuitive JSON template for LLMs without raw $defs or JSON schema noise,
    preventing smaller models from regurgitating schema definitions.
    """
    if hasattr(schema, "model_fields"):
        template = {k: _build_field_example(k, v) for k, v in schema.model_fields.items()}
        return json.dumps(template, indent=2)
    return "{}"


def generate_structured_output(
    prompt: str,
    schema: Type[T],
    system_prompt: Optional[str] = None,
    temperature: float = 0.0,
    model: Optional[str] = None
) -> T:
    """
    Invokes the LLM and strictly parses and validates the response against a Pydantic schema.
    Uses json_object response format with clean JSON template instructions.
    """
    client = get_openai_client()
    template_str = build_json_template_example(schema)

    sys_content = system_prompt or "You are an expert advertising intelligence agent."
    sys_content += (
        f"\n\nCRITICAL OUTPUT FORMAT INSTRUCTION:\n"
        f"You must return ONLY a populated JSON object matching this structure (fill with actual advertising data, NOT schema descriptions):\n"
        f"{template_str}\n"
        f"DO NOT include markdown code blocks, do NOT output keys like '$defs' or 'properties', and do NOT output an empty schema."
    )

    response = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": sys_content},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=temperature
    )

    raw_content = response.choices[0].message.content or "{}"
    parsed_json = json.loads(raw_content)

    # Recovery logic: if model wrapped output in a container key or accidentally returned properties
    if isinstance(parsed_json, dict):
        if "properties" in parsed_json and any(k in parsed_json["properties"] for k in schema.model_fields):
            extracted = {}
            for k, val in parsed_json["properties"].items():
                if isinstance(val, dict) and "default" in val:
                    extracted[k] = val["default"]
                elif isinstance(val, dict) and "description" in val:
                    extracted[k] = val["description"]
                else:
                    extracted[k] = val
            parsed_json = extracted
        elif len(parsed_json) == 1 and not any(k in parsed_json for k in schema.model_fields):
            single_val = next(iter(parsed_json.values()))
            if isinstance(single_val, dict):
                parsed_json = single_val

    return schema.model_validate(parsed_json)
