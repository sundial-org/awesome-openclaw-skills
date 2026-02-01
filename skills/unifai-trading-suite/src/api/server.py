"""FastAPI server for the trading agent."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.agents.trading_agent import TradingAgent


# Store agent instances per session (simple in-memory for demo)
agents: dict[str, TradingAgent] = {}


def get_or_create_agent(session_id: str) -> TradingAgent:
    """Get or create an agent for a session."""
    if session_id not in agents:
        agents[session_id] = TradingAgent()
    return agents[session_id]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("Starting AI Trading Agent API...")
    yield
    print("Shutting down...")
    agents.clear()


app = FastAPI(
    title="AI Trading Agent",
    description="AI-powered trading agent for prediction markets",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    session_id: str


class AnalyzeRequest(BaseModel):
    """Token analysis request."""
    token: str
    session_id: str = "default"


@app.get("/")
async def root():
    """Serve the frontend."""
    return FileResponse("src/api/static/index.html")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the trading agent."""
    try:
        agent = get_or_create_agent(request.session_id)
        # Clear history for each chat to avoid accumulation issues
        agent.clear_history()
        response = await agent.chat(request.message)
        return ChatResponse(response=response, session_id=request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze", response_model=ChatResponse)
async def analyze_token(request: AnalyzeRequest):
    """Perform comprehensive token analysis."""
    try:
        agent = get_or_create_agent(request.session_id)
        response = await agent.analyze_token(request.token)
        return ChatResponse(response=response, session_id=request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trending")
async def get_trending(session_id: str = "default"):
    """Get trending tokens from KOL discussions."""
    try:
        agent = get_or_create_agent(session_id)
        agent.clear_history()
        response = await agent.get_trending_signals()
        return ChatResponse(response=response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sentiment")
async def get_sentiment(topic: str, session_id: str = "default"):
    """Get market sentiment for a topic."""
    try:
        agent = get_or_create_agent(session_id)
        agent.clear_history()
        response = await agent.get_market_sentiment(topic)
        return ChatResponse(response=response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear")
async def clear_session(session_id: str = "default"):
    """Clear conversation history for a session."""
    if session_id in agents:
        agents[session_id].clear_history()
    return {"status": "cleared", "session_id": session_id}


# =========================================================================
# Polymarket Endpoints
# =========================================================================

@app.get("/api/polymarket/trending")
async def get_polymarket_trending(session_id: str = "default"):
    """Get trending events from Polymarket."""
    try:
        agent = get_or_create_agent(session_id)
        response = await agent.get_polymarket_trending()
        return ChatResponse(response=response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/polymarket/crypto")
async def get_polymarket_crypto(session_id: str = "default"):
    """Get crypto markets from Polymarket."""
    try:
        agent = get_or_create_agent(session_id)
        response = await agent.get_polymarket_crypto()
        return ChatResponse(response=response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/polymarket/search")
async def search_polymarket(query: str, session_id: str = "default"):
    """Search Polymarket markets."""
    try:
        agent = get_or_create_agent(session_id)
        response = await agent.search_polymarket(query)
        return ChatResponse(response=response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================================
# Kalshi Endpoints
# =========================================================================

@app.get("/api/kalshi/fed")
async def get_kalshi_fed(session_id: str = "default", limit: int = 10):
    """Get Federal Reserve interest rate markets from Kalshi."""
    try:
        agent = get_or_create_agent(session_id)
        response = await agent.get_fed_prediction_markets()
        return ChatResponse(response=response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/kalshi/economics")
async def get_kalshi_economics(session_id: str = "default", limit: int = 10):
    """Get economics markets (GDP, CPI) from Kalshi."""
    try:
        agent = get_or_create_agent(session_id)
        response = await agent.get_economics_prediction_markets()
        return ChatResponse(response=response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/kalshi/search")
async def search_kalshi(query: str, session_id: str = "default", limit: int = 10):
    """Search Kalshi markets."""
    try:
        agent = get_or_create_agent(session_id)
        markets = await agent.search_kalshi(query, limit=limit)
        formatted = agent._format_kalshi_markets(markets, f"Search: {query}")
        return ChatResponse(response=formatted, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================================
# Combined Endpoints
# =========================================================================

@app.get("/api/compare")
async def compare_platforms(topic: str, session_id: str = "default"):
    """Compare prediction markets from both Polymarket and Kalshi."""
    try:
        agent = get_or_create_agent(session_id)
        agent.clear_history()
        response = await agent.compare_platforms(topic)
        return ChatResponse(response=response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/markets")
async def get_all_markets(topic: str, session_id: str = "default"):
    """Get prediction markets from both platforms for a topic."""
    try:
        agent = get_or_create_agent(session_id)
        agent.clear_history()
        response = await agent.get_prediction_markets(topic)
        return ChatResponse(response=response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "unifai_configured": bool(os.getenv("UNIFAI_AGENT_API_KEY")),
        "google_configured": bool(os.getenv("GOOGLE_API_KEY")),
        "platforms": ["polymarket", "kalshi"],
    }


# Mount static files
app.mount("/static", StaticFiles(directory="src/api/static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
