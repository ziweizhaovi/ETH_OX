import aiohttp
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class CoinGeckoAPI:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        
    async def get_avax_price(self) -> Optional[float]:
        """Fetch real-time AVAX/USDC price from CoinGecko"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/simple/price"
                params = {
                    "ids": "avalanche-2",
                    "vs_currencies": "usd",
                    "include_24hr_change": "true"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = data.get("avalanche-2", {}).get("usd")
                        price_change = data.get("avalanche-2", {}).get("usd_24h_change")
                        
                        return {
                            "price": price,
                            "price_change_24h": price_change
                        }
                    else:
                        logger.error(f"CoinGecko API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error fetching AVAX price: {str(e)}")
            return None 