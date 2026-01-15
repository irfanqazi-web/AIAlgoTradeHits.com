"""
AIAlgoTradeHits - Multi-Agent Trading System
Autonomous AI agents for trading signals, risk management, and portfolio optimization
"""

__version__ = "1.0.0"
__author__ = "AIAlgoTradeHits"

from .orchestrator.agent_orchestrator import AgentOrchestrator
from .agents.base_agent import BaseAgent
from .agents.signal_generator import SignalGeneratorAgent
from .agents.risk_manager import RiskManagerAgent
from .agents.portfolio_manager import PortfolioManagerAgent

__all__ = [
    'AgentOrchestrator',
    'BaseAgent',
    'SignalGeneratorAgent',
    'RiskManagerAgent',
    'PortfolioManagerAgent'
]
