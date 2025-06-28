from os import getenv
from typing import Optional

from pydantic_settings import BaseSettings


class AgentSettings(BaseSettings):
    """تنظیمات ایجنت که می‌تواند با متغیرهای محیطی تنظیم شود.

    مرجع: https://pydantic-docs.helpmanual.io/usage/settings/
    """


    # تنظیمات OpenAI
    openai_api_key: str = getenv("OPENAI_API_KEY", "")

    # تنظیمات OpenRouter
    openrouter_api_key: str = getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = getenv("DEFAULT_OPENROUTER_MODEL", "openai/gpt-4o-mini")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # مدل‌های پیش‌فرض
    default_model_provider: str = getenv("DEFAULT_MODEL", "openai")
    default_model_id: str = getenv("DEFAULT_MODEL_ID", "gpt-4o-mini")

    # مدل‌های GPT
    gpt_4: str = "gpt-4o-mini"
    gpt_35: str = "gpt-3.5-turbo"

    # مدل‌های Gemini
    gemini_model: str = "gemini-exp-1206"

    # تنظیمات پیش‌فرض مدل
    default_temperature: float = 0.7
    default_max_completion_tokens: int = 4096

    # تنظیمات برنامه
    runtime_env: str = getenv("RUNTIME_ENV", "dev")
    app_domain: str = getenv("APP_DOMAIN", "http://localhost:8501")
    storage_dir: str = getenv("STORAGE_DIR", "/app/storage")
    charts_dir: str = getenv("CHARTS_DIR", "/app/storage/charts")
    static_url: str = getenv("STATIC_URL", "/static")

    # تنظیمات دیتابیس
    db_host: Optional[str] = getenv("DB_HOST")
    db_port: Optional[int] = int(getenv("DB_PORT", "5432"))
    db_user: Optional[str] = getenv("DB_USER")
    db_pass: Optional[str] = getenv("DB_PASS")
    db_database: Optional[str] = getenv("DB_DATABASE")

    # تنظیمات دیتابیس برداری
    vector_db_type: str = getenv("VECTOR_DB_TYPE", "postgres")
    pinecone_api_key: Optional[str] = getenv("PINECONE_API_KEY")
    pinecone_index: Optional[str] = getenv("PINECONE_INDEX")
    pinecone_host: Optional[str] = getenv("PINECONE_HOST")

    # سایر تنظیمات
    debug: bool = getenv("DEBUG", "True").lower() == "true"
    log_level: str = getenv("LOG_LEVEL", "INFO")

    def validate_settings(self):
        print("Validating settings...")
        print(f"OpenRouter API Key: {self.openrouter_api_key[:10]}...")
        print(f"OpenRouter Model: {self.openrouter_model}")
        print(f"App Domain: {self.app_domain}")
        
        # بررسی اینکه app_domain درست تنظیم شده باشد
        if not self.app_domain.startswith("http://") and not self.app_domain.startswith("https://"):
            print("Warning: App Domain is not a valid URL.")
        else:
            print("App Domain is valid.")

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""
        extra = "allow"  # اجازه وجود فیلدهای اضافی


# ایجاد شیء AgentSettings
agent_settings = AgentSettings()
