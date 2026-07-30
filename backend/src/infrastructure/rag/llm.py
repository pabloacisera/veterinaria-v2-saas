from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel


def get_llm(provider: str, model: str) -> BaseChatModel:
    provider = provider.lower()

    if provider == "openai":
        return ChatOpenAI(model=model or "gpt-4o-mini", streaming=True)
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(model=model or "gemini-1.5-flash", streaming=True)
    elif provider == "groq":
        return ChatGroq(model=model or "llama-3.3-70b-versatile", streaming=True)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
