from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class PriceFeedConfig(BaseSettings):
    COINGECKO_API_KEY: str = ""  # Optional, can be empty for public API
    COINGECKO_PRO_URL: str = "https://pro-api.coingecko.com/api/v3"
    COINGECKO_PUBLIC_URL: str = "https://api.coingecko.com/api/v3"
    CACHE_DURATION_SECONDS: int = 30
    
    model_config = ConfigDict(
        env_file=".env",
        extra="allow"  # Allow extra fields from environment
    )

price_feed_config = PriceFeedConfig() 