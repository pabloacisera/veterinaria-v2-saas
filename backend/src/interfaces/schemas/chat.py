from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str


class ChatHistoryItem(BaseModel):
    role: str
    content: str
    timestamp: str


class ChatHistoryResponse(BaseModel):
    history: list[ChatHistoryItem]


class ChatQuotaResponse(BaseModel):
    usado: int = 0
    limite: int = 0
    plan: str = ""
    reset_en: str = ""
