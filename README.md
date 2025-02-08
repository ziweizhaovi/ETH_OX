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

## Project Setup Guide

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/ziweizhaovi/ETH_OX.git
cd ETH_OX
```

### 2. Backend Setup

#### 2.1 Create and Activate Python Virtual Environment
```bash
cd backend
python -m venv venv

# On Windows
.\venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

#### 2.2 Install Backend Dependencies
```bash
pip install -r requirements.txt
```

#### 2.3 Set up Environment Variables
Create a `.env` file in the `backend` directory with the following content:
```env
# API Configuration
API_VERSION=v1
DEBUG=True
ENVIRONMENT=development

# Server Configuration
HOST=0.0.0.0
PORT=8000

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
```
Replace `your-openai-api-key-here` with your actual OpenAI API key.

#### 2.4 Run the Backend Server
```bash
# Make the run script executable (macOS/Linux only)
chmod +x run.sh

# Start the server
./run.sh

# Alternative command if run.sh doesn't work
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

### 3. Frontend Setup

#### 3.1 Install Frontend Dependencies
```bash
cd frontend
npm install
# or
yarn install
```

#### 3.2 Run the Frontend Development Server
```bash
npm run dev
# or
yarn dev
```

### 4. Verify the Setup

1. Backend API should be running at: `http://localhost:8000`
   - Visit `http://localhost:8000/docs` to see the API documentation
   - You should see "Welcome to ETH_OX API" at `http://localhost:8000`

2. Frontend should be running at: `http://localhost:3000`
   - You should see the main dashboard with the AI chat interface

### Common Issues and Solutions

1. **OpenAI API Key Issues**
   - Make sure your OpenAI API key is correctly set in the `.env` file
   - The key should start with 'sk-'

2. **Port Already in Use**
   - If port 8000 is in use, you can kill the process:
     ```bash
     # On macOS/Linux
     lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
     
     # On Windows
     netstat -ano | findstr :8000
     taskkill /PID <PID> /F
     ```

3. **Python Import Errors**
   - Make sure you're in the virtual environment (you should see `(venv)` in your terminal)
   - Try reinstalling dependencies: `pip install -r requirements.txt`

4. **Node.js Dependencies Issues**
   - Clear npm cache: `npm cache clean --force`
   - Delete `node_modules` and reinstall: 
     ```bash
     rm -rf node_modules
     npm install
     ```

### Project Structure
```
ETH_OX/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality
│   │   └── main.py       # Main application file
│   ├── venv/             # Python virtual environment
│   ├── .env              # Environment variables
│   └── requirements.txt  # Python dependencies
│
└── frontend/             # Next.js frontend
    ├── app/             # Next.js 13+ app directory
    ├── components/      # React components
    ├── hooks/          # Custom React hooks
    └── package.json    # Node.js dependencies
```

### Need Help?
If you encounter any issues not covered here, please:
1. Check the error logs
2. Make sure all environment variables are set correctly
3. Verify you're using the correct versions of Python and Node.js
4. Contact the team for support

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