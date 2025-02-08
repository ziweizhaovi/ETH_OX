# ETH_OX - AI-Powered DeFi Position Management

A modern DeFi platform that enables users to manage trading positions using natural language commands, powered by AI.

## Core Features

- 🤖 AI Trading Assistant - Natural language command processing for trade management
- 📈 Trade Execution - Seamless interaction with GMX smart contracts
- ⚠️ Risk Alerts - AI-powered monitoring of market conditions and position risks
- 🎯 Simple UI - Intuitive dashboard for position tracking and market analysis

## Project Structure

```
ETH_OX/
├── frontend/              # V0-based React/TypeScript frontend
├── backend/              # Python FastAPI backend
├── blockchain/          # Smart contract integration
└── shared/             # Shared types and utilities
```

## Getting Started

### Prerequisites

- Node.js >= 18
- Python >= 3.10
- npm (comes with Node.js)

### Setup Instructions

1. Clone the repository
```bash
git clone https://github.com/yourusername/ETH_OX.git
cd ETH_OX
```

2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

3. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## Development

- Frontend runs on http://localhost:3000
- Backend API runs on http://localhost:8000
- API documentation available at http://localhost:8000/docs

## Environment Setup

1. Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_API_VERSION=v1
VITE_CHAIN_ID=42161
VITE_GMX_ROUTER_ADDRESS=your_contract_address
VITE_WALLET_CONNECT_PROJECT_ID=your_project_id
```

2. Backend (.env)
```
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/eth_ox_db
SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_api_key
WEB3_PROVIDER_URL=https://arb1.arbitrum.io/rpc
```

## Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add some amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.