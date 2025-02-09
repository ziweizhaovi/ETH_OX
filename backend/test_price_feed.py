import asyncio
from app.core.price_feed.coingecko import CoinGeckoPriceFeed
from app.core.price_feed.config import price_feed_config

async def test_price_feed():
    price_feed = CoinGeckoPriceFeed()
    
    api_type = "Pro" if price_feed_config.COINGECKO_API_KEY else "Public"
    print(f"\nTesting CoinGecko Price Feed ({api_type} API):\n")

    # Test current price
    print("1. Testing current price:")
    avax_price = await price_feed.get_token_price("AVAX")
    print(f"AVAX price: ${avax_price}")
    
    # Test cached price
    print("\n2. Testing price caching:")
    cached_price = await price_feed.get_token_price("AVAX")
    print(f"Cached AVAX price: ${cached_price}")
    print(f"Cache duration: {price_feed_config.CACHE_DURATION_SECONDS} seconds")
    
    # Test market data
    print("\n3. Testing market data:")
    market_data = await price_feed.get_market_data("AVAX")
    if market_data:
        print(f"24h Change: {market_data['price_change_24h']}%")
        print(f"24h High: ${market_data['high_24h'].get('usd')}")
        print(f"24h Low: ${market_data['low_24h'].get('usd')}")
        print(f"24h Volume: ${market_data['total_volume'].get('usd'):,.2f}")
    
    # Test price history
    print("\n4. Testing price history (last 24h):")
    history = await price_feed.get_token_price_history("AVAX", days=1)
    if history and history['prices']:
        latest_price = history['prices'][-1][1]
        earliest_price = history['prices'][0][1]
        print(f"24h ago: ${earliest_price:.2f}")
        print(f"Latest: ${latest_price:.2f}")
        print(f"Price change: {((latest_price - earliest_price) / earliest_price * 100):.2f}%")
        print(f"Number of price points: {len(history['prices'])}")
    else:
        print("Price history not available (requires Pro API key)")

if __name__ == "__main__":
    asyncio.run(test_price_feed()) 