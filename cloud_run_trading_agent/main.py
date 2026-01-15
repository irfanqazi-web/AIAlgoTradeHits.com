"""
Trading Agent Cloud Run Service
AIAlgoTradeHits.com - Agentic AI API
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import agent modules
try:
    from shared_ai_modules.base_agent import TradingAgent, AgentConfig
    from shared_ai_modules.memory import AgentMemory
    from shared_ai_modules.tools import TradingTools
    from shared_ai_modules.orchestrator import TradingOrchestrator
    from shared_ai_modules.evaluator import TradingAgentEvaluator
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Agent modules not fully available: {e}")
    AGENTS_AVAILABLE = False

# Initialize components
tools = TradingTools()
orchestrator = TradingOrchestrator()
evaluator = TradingAgentEvaluator()

# User sessions (in production, use Redis or Firestore)
user_sessions: Dict[str, Dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("Trading Agent API starting up...")
    print(f"Agents available: {AGENTS_AVAILABLE}")
    yield
    print("Trading Agent API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="AIAlgoTradeHits Trading Agent API",
    description="Agentic AI Trading Assistant powered by Claude",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ChatRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[Dict] = None


class ChatResponse(BaseModel):
    response: str
    tool_calls: List[Dict] = []
    session_id: str
    timestamp: str


class GrowthScoreRequest(BaseModel):
    symbol: str


class RiseCycleRequest(BaseModel):
    symbol: str


class MarketDataRequest(BaseModel):
    symbol: str
    interval: str = "1day"


class AlertRequest(BaseModel):
    symbol: str
    signal: str
    message: str


class WorkflowRequest(BaseModel):
    workflow_name: str
    params: Optional[Dict] = None


# Health check
@app.get("/")
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "trading-agent",
        "version": "1.0.0",
        "agents_available": AGENTS_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }


# Chat with Trading Agent
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Chat with the AI Trading Agent.
    The agent can analyze markets, calculate Growth Scores,
    detect rise cycles, and provide trading insights.
    """
    if not AGENTS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Agent modules not available"
        )

    start_time = datetime.now()

    try:
        # Get or create user session
        if request.user_id not in user_sessions:
            memory = AgentMemory(user_id=request.user_id, project="trading")
            user_sessions[request.user_id] = {
                "memory": memory,
                "created_at": datetime.now().isoformat()
            }

        memory = user_sessions[request.user_id]["memory"]

        # Create agent with user's memory
        agent = TradingAgent(memory=memory)

        # Run the agent
        response = await agent.run(request.message)

        # Log metrics
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()

        background_tasks.add_task(
            evaluator.log_interaction,
            response_time=response_time,
            tool_calls=len(agent.metrics[-1].get("tool_calls", 0)) if agent.metrics else 0,
            tokens_used=0,  # Would need to track from API response
            success=True
        )

        return ChatResponse(
            response=response,
            tool_calls=[],  # Could extract from agent.conversation_history
            session_id=request.user_id,
            timestamp=end_time.isoformat()
        )

    except Exception as e:
        evaluator.log_interaction(
            response_time=(datetime.now() - start_time).total_seconds(),
            tool_calls=0,
            tokens_used=0,
            success=False,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))


# Growth Score calculation
@app.post("/growth-score")
async def calculate_growth_score(request: GrowthScoreRequest):
    """Calculate Growth Score for a symbol"""
    result = tools.calculate_growth_score({"symbol": request.symbol})

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# Rise cycle detection
@app.post("/rise-cycle")
async def detect_rise_cycle(request: RiseCycleRequest):
    """Detect rise/fall cycle for a symbol"""
    result = tools.detect_rise_cycle({"symbol": request.symbol})

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# Market data
@app.post("/market-data")
async def get_market_data(request: MarketDataRequest):
    """Get market data and indicators for a symbol"""
    result = tools.get_market_data({
        "symbol": request.symbol,
        "interval": request.interval
    })

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# Rise cycle candidates
@app.get("/rise-cycle-candidates")
async def get_rise_cycle_candidates(
    asset_type: str = "all",
    limit: int = 20
):
    """Get assets that recently entered a rise cycle"""
    result = tools.get_rise_cycle_candidates({
        "asset_type": asset_type,
        "limit": limit
    })

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# Top Growth Scores
@app.get("/top-growth-scores")
async def get_top_growth_scores(
    min_score: int = 75,
    limit: int = 20
):
    """Get assets with highest Growth Scores"""
    result = tools.get_top_growth_scores({
        "min_score": min_score,
        "limit": limit
    })

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# Send alert
@app.post("/send-alert")
async def send_alert(request: AlertRequest):
    """Send a trading alert"""
    result = tools.send_alert({
        "symbol": request.symbol,
        "signal": request.signal,
        "message": request.message
    })

    return result


# Execute workflow
@app.post("/workflow")
async def execute_workflow(request: WorkflowRequest):
    """Execute a pre-defined trading workflow"""
    try:
        result = await orchestrator.execute_workflow(
            request.workflow_name,
            request.params or {}
        )

        return {
            "status": result.status.value,
            "results": result.results,
            "errors": result.errors,
            "execution_time": result.execution_time
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get available workflows
@app.get("/workflows")
async def list_workflows():
    """List available trading workflows"""
    return {
        "workflows": list(orchestrator.workflows.keys()),
        "descriptions": {
            "full_analysis": "Complete market analysis with technical indicators",
            "quick_screen": "Quick screening for opportunities",
            "rise_cycle_detection": "Detect new rise cycle entries",
            "portfolio_review": "Review portfolio and risk assessment"
        }
    }


# Agent metrics
@app.get("/metrics")
async def get_metrics():
    """Get agent performance metrics"""
    return {
        "performance": evaluator.analyze_performance(),
        "error_analysis": evaluator.get_error_analysis(),
        "workflow_stats": orchestrator.get_workflow_stats()
    }


# Generate report
@app.get("/report")
async def generate_report(days: int = 7):
    """Generate evaluation report"""
    report = evaluator.generate_report(days=days)

    return {
        "period_start": report.period_start,
        "period_end": report.period_end,
        "total_interactions": report.total_interactions,
        "success_rate": report.success_rate,
        "avg_response_time": report.avg_response_time,
        "avg_tool_calls": report.avg_tool_calls,
        "error_rate": report.error_rate,
        "top_errors": report.top_errors,
        "recommendations": report.recommendations
    }


# Tool definitions (for client integration)
@app.get("/tools")
async def list_tools():
    """Get available tool definitions"""
    return {
        "tools": TradingTools.get_tool_definitions()
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
