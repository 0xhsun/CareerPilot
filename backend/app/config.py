from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # 104 人力銀行 base URL
    BASE_URL: str = "https://www.104.com.tw/jobs/search/api/jobs"

    # 預設爬取頁數
    DEFAULT_PAGES: int = 5

    # CORS 允許的來源（前端 URL）
    CORS_ORIGINS: list[str] = ["*"]

    # OpenAI API key (for AI job evaluation)
    OPENAI_API_KEY: str = ""

    # OpenAI-compatible API base URL. Empty = official OpenAI endpoint.
    # For OpenRouter: https://openrouter.ai/api/v1
    OPENAI_BASE_URL: str = ""

    # Chat model id. On OpenRouter this needs a vendor prefix, e.g. openai/gpt-5.4-mini
    OPENAI_MODEL: str = "gpt-5.4-mini"

    # Embedding model id used by the RAG pipeline (rag.py)
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Reasoning budget for gateways that support it (e.g. OpenRouter). Left unset,
    # nothing is sent — the right default for the official OpenAI API, which
    # rejects the extra field.
    #   "low" / "medium" / "high"  cap the thinking budget
    #   "none"                     disable reasoning outright
    # Unconstrained reasoning models can spend the whole max_completion_tokens
    # budget on their thinking trace and return empty content, so "low" is the
    # safe choice on OpenRouter. Note some models (e.g. Gemini 3.x Flash) reject
    # "none" with "Reasoning is mandatory for this endpoint".
    REASONING_EFFORT: str = ""

    # Debug mode
    DEBUG: bool = True

    # SQLite database path (relative to working directory when server starts)
    DB_PATH: str = "evaluations.db"

    # Alerts storage path; empty = default backend/alerts.json (next to the app package)
    ALERTS_FILE: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Area options for the frontend
AREA_OPTIONS = [
    {"value": "6001001000", "label": "台北市"},
    {"value": "6001002000", "label": "新北市"},
    {"value": "6001006000", "label": "新竹市"},
    {"value": "6001008000", "label": "台中市"},
    {"value": "6001014000", "label": "台南市"},
    {"value": "6001016000", "label": "高雄市"},
]

# Experience options for the frontend
EXPERIENCE_OPTIONS = [
    {"value": "1", "label": "1年以下"},
    {"value": "3", "label": "1-3年"},
    {"value": "5", "label": "3-5年"},
    {"value": "10", "label": "5-10年"},
    {"value": "99", "label": "10年以上"},
]


settings = Settings()
