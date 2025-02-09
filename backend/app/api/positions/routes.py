from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from decimal import Decimal
import random

router = APIRouter()

# Store mock positions in memory for testing
mock_positions = []

@router.get("")
async def get_positions(wallet_address: str = "0x1234567890123456789012345678901234567890"):
    """Get all positions for a wallet"""
    try:
        # For testing, return mock positions with updated prices
        for position in mock_positions:
            # Simulate price movement
            price_change = random.uniform(-0.5, 0.5)
            position['currentPrice'] = round(position['currentPrice'] + price_change, 2)
            # Update PnL
            if position['entryPrice'] > 0:
                price_diff = position['currentPrice'] - position['entryPrice']
                pnl_multiplier = 1 if position.get('type') == 'long' else -1
                position['pnl'] = round(price_diff / position['entryPrice'] * 100 * pnl_multiplier, 2)
        
        return mock_positions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mock/add")
async def add_mock_position(position: Dict):
    """Add a mock position for testing"""
    try:
        new_position = {
            "id": f"{position['type']}-{len(mock_positions) + 1}",
            "asset": "AVAX",
            "type": position['type'],
            "entryPrice": float(position.get('entryPrice', 25.0)),
            "currentPrice": float(position.get('currentPrice', 25.0)),
            "pnl": float(position.get('pnl', 0.0)),
            "leverage": float(position.get('leverage', 1.0))
        }
        
        # Only add if not already exists
        if not any(p['id'] == new_position['id'] for p in mock_positions):
            mock_positions.append(new_position)
        
        return {"status": "success", "positions": mock_positions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/mock/clear")
async def clear_mock_positions():
    """Clear all mock positions"""
    mock_positions.clear()
    return {"status": "success", "positions": mock_positions} 