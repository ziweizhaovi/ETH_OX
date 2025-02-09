from typing import Dict, List, Optional
from decimal import Decimal
import logging
from datetime import datetime, timedelta
import numpy as np
from ..db.service import DatabaseService
from ..db.models import Position, Order, PositionStatus
from ..price_feed.coingecko import CoinGeckoPriceFeed

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
        self.price_feed = CoinGeckoPriceFeed()

    async def get_performance_metrics(self, wallet_address: str) -> Dict:
        """Calculate comprehensive trading performance metrics."""
        try:
            # Get all closed positions
            positions = await self.db.get_position_history(
                wallet_address,
                status=PositionStatus.CLOSED
            )
            
            if not positions:
                return {
                    "status": "success",
                    "metrics": {
                        "total_trades": 0,
                        "win_rate": 0,
                        "total_pnl": 0,
                        "average_pnl": 0,
                        "best_trade": 0,
                        "worst_trade": 0,
                        "average_holding_time": 0,
                        "average_leverage": 0,
                        "risk_reward_ratio": 0
                    }
                }
            
            # Calculate metrics
            total_trades = len(positions)
            winning_trades = len([p for p in positions if p.pnl > 0])
            total_pnl = sum(p.pnl for p in positions)
            average_pnl = total_pnl / total_trades
            best_trade = max(p.pnl for p in positions)
            worst_trade = min(p.pnl for p in positions)
            
            # Calculate holding times
            holding_times = [
                (p.closed_at - p.created_at).total_seconds() / 3600  # hours
                for p in positions if p.closed_at
            ]
            average_holding_time = sum(holding_times) / len(holding_times)
            
            # Calculate risk metrics
            average_leverage = sum(p.leverage for p in positions) / total_trades
            
            # Risk/Reward ratio (absolute value of average win / average loss)
            winning_pnls = [p.pnl for p in positions if p.pnl > 0]
            losing_pnls = [abs(p.pnl) for p in positions if p.pnl < 0]
            risk_reward_ratio = (
                (sum(winning_pnls) / len(winning_pnls)) /
                (sum(losing_pnls) / len(losing_pnls))
                if losing_pnls else float('inf')
            )
            
            return {
                "status": "success",
                "metrics": {
                    "total_trades": total_trades,
                    "win_rate": (winning_trades / total_trades) * 100,
                    "total_pnl": float(total_pnl),
                    "average_pnl": float(average_pnl),
                    "best_trade": float(best_trade),
                    "worst_trade": float(worst_trade),
                    "average_holding_time": float(average_holding_time),
                    "average_leverage": float(average_leverage),
                    "risk_reward_ratio": float(risk_reward_ratio)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate performance metrics: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def analyze_risk_exposure(self, wallet_address: str) -> Dict:
        """Analyze current risk exposure across all positions."""
        try:
            # Get active positions
            positions = await self.db.get_position_history(
                wallet_address,
                status=PositionStatus.OPEN
            )
            
            if not positions:
                return {
                    "status": "success",
                    "risk_metrics": {
                        "total_exposure": 0,
                        "max_leverage": 0,
                        "weighted_avg_leverage": 0,
                        "long_exposure": 0,
                        "short_exposure": 0,
                        "largest_position": 0
                    }
                }
            
            # Calculate risk metrics
            total_exposure = sum(p.size for p in positions)
            max_leverage = max(p.leverage for p in positions)
            
            # Weighted average leverage
            weighted_avg_leverage = sum(
                p.leverage * p.size for p in positions
            ) / total_exposure
            
            # Directional exposure
            long_exposure = sum(p.size for p in positions if p.position_type == 'long')
            short_exposure = sum(p.size for p in positions if p.position_type == 'short')
            
            # Largest position
            largest_position = max(p.size for p in positions)
            
            return {
                "status": "success",
                "risk_metrics": {
                    "total_exposure": float(total_exposure),
                    "max_leverage": float(max_leverage),
                    "weighted_avg_leverage": float(weighted_avg_leverage),
                    "long_exposure": float(long_exposure),
                    "short_exposure": float(short_exposure),
                    "largest_position": float(largest_position),
                    "net_exposure": float(long_exposure - short_exposure),
                    "exposure_ratio": float(long_exposure / short_exposure if short_exposure else float('inf'))
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze risk exposure: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def calculate_drawdown(self, wallet_address: str) -> Dict:
        """Calculate maximum drawdown and current drawdown."""
        try:
            positions = await self.db.get_position_history(wallet_address)
            if not positions:
                return {
                    "status": "success",
                    "drawdown_metrics": {
                        "max_drawdown": 0,
                        "current_drawdown": 0,
                        "max_drawdown_duration": 0
                    }
                }
            
            # Sort positions by timestamp
            positions.sort(key=lambda x: x.created_at)
            
            # Calculate cumulative PnL
            cumulative_pnl = []
            current_pnl = 0
            for pos in positions:
                if pos.pnl:
                    current_pnl += pos.pnl
                    cumulative_pnl.append(current_pnl)
            
            if not cumulative_pnl:
                return {
                    "status": "success",
                    "drawdown_metrics": {
                        "max_drawdown": 0,
                        "current_drawdown": 0,
                        "max_drawdown_duration": 0
                    }
                }
            
            # Calculate maximum drawdown
            peak = cumulative_pnl[0]
            max_drawdown = 0
            current_drawdown = 0
            max_drawdown_duration = 0
            current_duration = 0
            
            for pnl in cumulative_pnl:
                if pnl > peak:
                    peak = pnl
                    current_duration = 0
                else:
                    current_duration += 1
                    drawdown = (peak - pnl) / peak if peak > 0 else 0
                    max_drawdown = max(max_drawdown, drawdown)
                    if current_duration > max_drawdown_duration:
                        max_drawdown_duration = current_duration
            
            # Calculate current drawdown
            if cumulative_pnl:
                current_drawdown = (max(cumulative_pnl) - cumulative_pnl[-1]) / max(cumulative_pnl) if max(cumulative_pnl) > 0 else 0
            
            return {
                "status": "success",
                "drawdown_metrics": {
                    "max_drawdown": float(max_drawdown * 100),  # as percentage
                    "current_drawdown": float(current_drawdown * 100),  # as percentage
                    "max_drawdown_duration": int(max_drawdown_duration)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate drawdown: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def analyze_market_correlation(self, wallet_address: str) -> Dict:
        """Analyze correlation between trading performance and market movements."""
        try:
            # Get position history
            positions = await self.db.get_position_history(wallet_address)
            if not positions:
                return {
                    "status": "success",
                    "correlation_metrics": {
                        "market_correlation": 0,
                        "volatility_correlation": 0,
                        "trend_alignment": 0
                    }
                }
            
            # Get market data for the trading period
            start_date = min(p.created_at for p in positions)
            end_date = max(p.closed_at or datetime.utcnow() for p in positions)
            days = (end_date - start_date).days + 1
            
            market_data = await self.price_feed.get_token_price_history("AVAX", days=days)
            if not market_data:
                raise ValueError("Failed to get market data")
            
            # Calculate daily returns
            prices = [p[1] for p in market_data['prices']]
            market_returns = np.diff(prices) / prices[:-1]
            
            # Calculate trading returns
            daily_pnl = {}
            for position in positions:
                if position.closed_at and position.pnl:
                    date = position.closed_at.date()
                    daily_pnl[date] = daily_pnl.get(date, 0) + position.pnl
            
            trading_returns = list(daily_pnl.values())
            
            # Calculate correlations
            if len(trading_returns) > 1 and len(market_returns) > 1:
                market_correlation = float(np.corrcoef(
                    trading_returns[:min(len(trading_returns), len(market_returns))],
                    market_returns[:min(len(trading_returns), len(market_returns))]
                )[0, 1])
                
                # Calculate volatility correlation
                market_volatility = np.std(market_returns)
                trading_volatility = np.std(trading_returns)
                volatility_correlation = market_volatility / trading_volatility if trading_volatility else 0
                
                # Calculate trend alignment
                market_trend = sum(1 for r in market_returns if r > 0) / len(market_returns)
                trading_trend = sum(1 for r in trading_returns if r > 0) / len(trading_returns)
                trend_alignment = abs(market_trend - trading_trend)
            else:
                market_correlation = 0
                volatility_correlation = 0
                trend_alignment = 0
            
            return {
                "status": "success",
                "correlation_metrics": {
                    "market_correlation": float(market_correlation),
                    "volatility_correlation": float(volatility_correlation),
                    "trend_alignment": float(trend_alignment)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze market correlation: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 