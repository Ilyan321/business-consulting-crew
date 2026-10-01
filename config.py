import _compat  # noqa: F401
import os
import time
from typing import Optional, Dict, Any
from crewai import LLM

# Disable telemetry and trace sharing prompts for headless/cloud environments
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "openai/gpt-oss-20b"

AVAILABLE_MODELS = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
]


def get_groq_api_key(explicit_key: Optional[str] = None) -> str:
    """
    Resolves the Groq API key with proper precedence:
    1. Explicit key provided by user (e.g. from UI input)
    2. Streamlit Cloud secrets (st.secrets["GROQ_API_KEY"])
    3. Environment variable (GROQ_API_KEY)
    """
    if explicit_key and explicit_key.strip():
        return explicit_key.strip()

    # Attempt retrieval from Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            secret_key = st.secrets["GROQ_API_KEY"]
            if secret_key and str(secret_key).strip():
                return str(secret_key).strip()
    except Exception:
        pass

    # Attempt retrieval from system environment variables
    env_key = os.environ.get("GROQ_API_KEY", "")
    if env_key and env_key.strip():
        return env_key.strip()

    return ""


def get_llm(
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
) -> LLM:
    """
    Initializes a modern CrewAI LLM instance configured for Groq's
    OpenAI-compatible endpoint.
    """
    resolved_key = get_groq_api_key(api_key)
    if not resolved_key:
        raise ValueError(
            "Groq API Key not found. Please provide it in Streamlit secrets (.streamlit/secrets.toml) "
            "or enter it in the sidebar."
        )

    # Set environment variables for internal LiteLLM / CrewAI compatibility
    os.environ["GROQ_API_KEY"] = resolved_key
    os.environ["OPENAI_API_BASE"] = GROQ_BASE_URL
    os.environ["OPENAI_API_KEY"] = resolved_key
    os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
    os.environ["OTEL_SDK_DISABLED"] = "true"

    clean_model = model.strip()
    # If model contains a slash (like openai/gpt-oss-120b or qwen/qwen3.8-27b),
    # prefix with 'openai/' so CrewAI uses openai provider and sends the full model name to Groq
    if not clean_model.startswith("openai/"):
        llm_model_param = f"openai/{clean_model}"
    else:
        # e.g. openai/gpt-oss-120b -> openai/openai/gpt-oss-120b
        llm_model_param = f"openai/{clean_model}"

    return LLM(
        model=llm_model_param,
        base_url=GROQ_BASE_URL,
        api_key=resolved_key,
        temperature=temperature,
    )


def test_groq_connection(api_key: str, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Tests connectivity to Groq using the OpenAI client.
    Supports both client.responses.create and client.chat.completions.create.
    """
    from openai import OpenAI

    if not api_key or not api_key.strip():
        return {
            "success": False,
            "error": "Groq API key cannot be empty.",
            "latency": 0.0,
        }

    start_time = time.time()
    try:
        client = OpenAI(
            api_key=api_key.strip(),
            base_url=GROQ_BASE_URL,
        )

        output_text = ""
        method_used = "responses.create"

        try:
            # User requested responses.create method
            response = client.responses.create(
                input="Explain the importance of fast language models in 2 concise sentences.",
                model=model,
            )
            output_text = getattr(response, "output_text", str(response))
        except Exception as e_resp:
            # Fallback to chat completions if responses endpoint is unsupported for this model
            method_used = "chat.completions.create"
            chat_model = model.replace("openai/", "")
            chat_response = client.chat.completions.create(
                model=chat_model,
                messages=[
                    {
                        "role": "user",
                        "content": "Explain the importance of fast language models in 2 concise sentences.",
                    }
                ],
                max_tokens=100,
            )
            output_text = chat_response.choices[0].message.content or ""

        latency = round(time.time() - start_time, 2)
        return {
            "success": True,
            "message": output_text.strip(),
            "latency": latency,
            "method": method_used,
            "model": model,
        }
    except Exception as e:
        latency = round(time.time() - start_time, 2)
        return {
            "success": False,
            "error": str(e),
            "latency": latency,
        }
