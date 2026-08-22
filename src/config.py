from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):

    bot_token: SecretStr
    admin_id: int
    database_url: str
    dadata_api_key: SecretStr
    dadata_secret_key: SecretStr
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()