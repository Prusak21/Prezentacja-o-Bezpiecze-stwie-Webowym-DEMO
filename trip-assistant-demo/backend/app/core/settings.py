from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    JWT_SECRET: str  # wymagany, brak wartości domyślnej: sekret tylko z .env / środowiska
    CORS_ORIGINS: str = "http://localhost:5173"
    DATABASE_URL: str = "sqlite:///./trip.db"
    ACCESS_TOKEN_MINUTES: int = 60
    IDOR_STATUS: int = 404  # status dla cudzych zasobów: 404 (ukrywa istnienie) lub 403
    DEMO_VULNERABLE_IDOR: bool = False  # TYLKO do pokazu luki, domyślnie wyłączone

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()

