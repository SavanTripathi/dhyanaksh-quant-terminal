from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "HTF-Zone-Scanner-Terminal"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite+aiosqlite:///./htf_scanner.db"
    
    # Session parameters (IST)
    MARKET_OPEN_HOUR: int = 9
    MARKET_OPEN_MINUTE: int = 15
    MARKET_CLOSE_HOUR: int = 15
    MARKET_CLOSE_MINUTE: int = 30
    
    # Zone parameters
    ERC_BODY_RATIO: float = 0.50  # Candle body > 50% is institutional ERC
    MAX_BASE_CANDLES: int = 6     # Maximum basing candles allowed for institutional quality
    MIN_ACHIEVEMENTS: int = 2     # Minimum overlapping timeframes for confluence (Tier 2/3)

    model_config = SettingsConfigDict(case_sensitive=True)


settings = Settings()
