from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    tmdb_api_key: str
    tmdb_language: str = "uk-UA"
    tmdb_fallback_language: str = "en-US"
    log_level: str = "INFO"
    scraper_base_url: str
    selenium_url: str = "http://selenium:4444/wd/hub"


settings = Settings()
