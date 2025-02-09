from typing import Dict, Optional
import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta
from .config import price_feed_config

logger = logging.getLogger(__name__)

class CoinGeckoPriceFeed:
    def __init__(self):
        self.base_url = (
            price_feed_config.COINGECKO_PRO_URL 
            if price_feed_config.COINGECKO_API_KEY 
            else price_feed_config.COINGECKO_PUBLIC_URL
        )
        self.price_cache: Dict[str, Dict] = {}
        self.cache_duration = timedelta(seconds=price_feed_config.CACHE_DURATION_SECONDS)
        self.supported_tokens = {
            "AVAX": "avalanche-2",
            "USDC": "usd-coin"
        }

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Accept": "application/json",
        }
        if price_feed_config.COINGECKO_API_KEY:
            headers["X-Cg-Pro-Api-Key"] = price_feed_config.COINGECKO_API_KEY
        return headers

    async def get_token_price(self, token: str, vs_currency: str = "usd") -> Optional[float]:
        """Get the current price of a token in the specified currency."""
        token = token.upper()
        if token not in self.supported_tokens:
            logger.error(f"Unsupported token: {token}")
            return None

        # Check cache first
        cache_key = f"{token}_{vs_currency}"
        if cache_key in self.price_cache:
            cached_data = self.price_cache[cache_key]
            if datetime.now() - cached_data["timestamp"] < self.cache_duration:
                logger.debug(f"Returning cached price for {token}: {cached_data['price']}")
                return cached_data["price"]

        # Fetch new price
        try:
            coin_id = self.supported_tokens[token]
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/simple/price"
                params = {
                    "ids": coin_id,
                    "vs_currencies": vs_currency
                }
                
                async with session.get(url, params=params, headers=self._get_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = data[coin_id][vs_currency]
                        
                        # Update cache
                        self.price_cache[cache_key] = {
                            "price": price,
                            "timestamp": datetime.now()
                        }
                        
                        logger.info(f"Updated price for {token}: {price} {vs_currency.upper()}")
                        return price
                    else:
                        logger.error(f"Failed to fetch price for {token}. Status: {response.status}")
                        return None

        except Exception as e:
            logger.error(f"Error fetching price for {token}: {str(e)}")
            return None

    async def get_token_price_history(self, token: str, days: int = 1, vs_currency: str = "usd") -> Optional[Dict]:
        """Get historical price data for a token."""
        token = token.upper()
        if token not in self.supported_tokens:
            logger.error(f"Unsupported token: {token}")
            return None

        try:
            coin_id = self.supported_tokens[token]
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/coins/{coin_id}/market_chart"
                params = {
                    "vs_currency": vs_currency,
                    "days": days,
                    "interval": "hourly" if days <= 7 else "daily"
                }
                
                async with session.get(url, params=params, headers=self._get_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "prices": data["prices"],
                            "market_caps": data["market_caps"],
                            "total_volumes": data["total_volumes"]
                        }
                    elif response.status == 401 and not price_feed_config.COINGECKO_API_KEY:
                        logger.warning("CoinGecko API key required for historical data. Using public API fallback...")
                        # Fallback to simpler endpoint for public API
                        url = f"{self.base_url}/coins/{coin_id}"
                        async with session.get(url, headers=self._get_headers()) as fallback_response:
                            if fallback_response.status == 200:
                                data = await fallback_response.json()
                                market_data = data.get("market_data", {})
                                return {
                                    "prices": [[datetime.now().timestamp() * 1000, market_data.get("current_price", {}).get("usd")]],
                                    "market_caps": [[datetime.now().timestamp() * 1000, market_data.get("market_cap", {}).get("usd")]],
                                    "total_volumes": [[datetime.now().timestamp() * 1000, market_data.get("total_volume", {}).get("usd")]]
                                }
                    else:
                        logger.error(f"Failed to fetch price history for {token}. Status: {response.status}")
                        return None

        except Exception as e:
            logger.error(f"Error fetching price history for {token}: {str(e)}")
            return None

    async def get_market_data(self, token: str) -> Optional[Dict]:
        """Get detailed market data for a token including 24h change, volume, etc."""
        token = token.upper()
        if token not in self.supported_tokens:
            logger.error(f"Unsupported token: {token}")
            return None

        try:
            coin_id = self.supported_tokens[token]
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/coins/{coin_id}"
                params = {
                    "localization": "false",
                    "tickers": "false",
                    "community_data": "false",
                    "developer_data": "false"
                }
                
                async with session.get(url, params=params, headers=self._get_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        market_data = data.get("market_data", {})
                        return {
                            "current_price": market_data.get("current_price", {}),
                            "price_change_24h": market_data.get("price_change_percentage_24h"),
                            "market_cap": market_data.get("market_cap", {}),
                            "total_volume": market_data.get("total_volume", {}),
                            "high_24h": market_data.get("high_24h", {}),
                            "low_24h": market_data.get("low_24h", {})
                        }
                    else:
                        logger.error(f"Failed to fetch market data for {token}. Status: {response.status}")
                        return None

        except Exception as e:
            logger.error(f"Error fetching market data for {token}: {str(e)}")
            return None 