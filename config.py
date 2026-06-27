from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    database_url: str
    app_env: str = "development"
    debug: bool = False

    jwt_algorithm: str
    jwt_expiry_minutes: float
    jwt_secret: str
    jwt_refresh_expiry_minutes: float

    model_config = SettingsConfigDict(env_file=".env")


setting = Setting()
