import os
from backend.config import settings

def get_llm():
    """
    Returns the configured LLM instance for CrewAI.
    Prioritizes Gemini API when GEMINI_API_KEY is configured.
    Falls back gracefully to standard CrewAI LLM or local deterministic provider.
    """
    api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
    provider = settings.LLM_PROVIDER.lower()
    
    if api_key and provider in ["gemini", "google"]:
        from crewai import LLM
        os.environ["GEMINI_API_KEY"] = api_key
        # CrewAI LLM format for Gemini
        model_name = settings.LLM_MODEL if "/" in settings.LLM_MODEL else f"gemini/{settings.LLM_MODEL}"
        return LLM(model=model_name, api_key=api_key)
    
    # If OPENAI_API_KEY is present
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        from crewai import LLM
        return LLM(model="gpt-4o-mini", api_key=openai_key)

    # If no external API key is provided, configure CrewAI LLM with dummy/mock or local
    # For standalone environments without external keys, return None so crew runner can use verified deterministic logic
    return None
