import asyncio
from decimal import Decimal
from web3 import Web3
from app.core.gmx.client import GMXClient
from app.core.gmx.config import gmx_config

async def test_gmx():
    client = GMXClient()
    
    print("\nTesting GMX Integration:\n")

    # Test token addresses
    print("1. Configured Token Addresses:")
    for token, address in gmx_config.TOKEN_ADDRESSES.items():
        print(f"{token}: {address}")
    
    # Test available liquidity
    print("\n2. Testing Available Liquidity:")
    try:
        avax_liquidity = client.get_available_liquidity("AVAX")
        usdc_liquidity = client.get_available_liquidity("USDC")
        print(f"AVAX Liquidity: {Web3.from_wei(avax_liquidity, 'ether')} AVAX")
        print(f"USDC Liquidity: {Web3.from_wei(usdc_liquidity, 'mwei')} USDC")  # USDC has 6 decimals
    except Exception as e:
        print(f"Error getting liquidity: {str(e)}")
    
    # Test position calculations
    print("\n3. Testing Position Calculations:")
    try:
        # Example position parameters
        size = Web3.to_wei(Decimal('1000'), 'ether') * 10**12  # $1000 position
        collateral = Web3.to_wei(Decimal('100'), 'ether') * 10**12  # $100 collateral
        avg_price = Web3.to_wei(Decimal('25'), 'ether')  # $25 entry price
        
        # Calculate leverage
        leverage = client.get_position_leverage(size, collateral, avg_price)
        print(f"Position Leverage: {leverage}x")
        
        # Calculate liquidation price
        liq_price_long = client.get_liquidation_price(size, collateral, avg_price, True)
        liq_price_short = client.get_liquidation_price(size, collateral, avg_price, False)
        print(f"Long Position Liquidation Price: ${liq_price_long:.2f}")
        print(f"Short Position Liquidation Price: ${liq_price_short:.2f}")
    except Exception as e:
        print(f"Error calculating position metrics: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_gmx()) 