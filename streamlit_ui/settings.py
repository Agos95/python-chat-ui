from pydantic_settings import BaseSettings, SettingsConfigDict


class BackendConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BACKEND", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    BASE_URL: str = "http://localhost:8000"


class UIConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="UI", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    APP_TITLE: str = "Chat App"
    APP_FAVICON: str = ":robot_face:"
    DEFAULT_CHAT_TITLE: str = "New Chat"


backend_settings = BackendConfig()
ui_settings = UIConfig()
