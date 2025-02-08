from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.ai_agent.routes import router as ai_router

app = FastAPI(
    title="ETH_OX API",
    description="Backend API for ETH_OX DeFi Position Management Platform",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to ETH_OX API"}

# Import and include routers
# from app.api.routes import trades, positions, market_data

# app.include_router(trades.router, prefix="/api/v1/trades", tags=["trades"])
# app.include_router(positions.router, prefix="/api/v1/positions", tags=["positions"])
# app.include_router(market_data.router, prefix="/api/v1/market", tags=["market"])

# Include AI agent router
app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"]) 