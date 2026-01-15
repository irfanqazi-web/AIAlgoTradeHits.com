"""Agent modules for the Multi-Agent Trading System"""

from .base_agent import BaseAgent
from .signal_generator import SignalGeneratorAgent
from .risk_manager import RiskManagerAgent
from .portfolio_manager import PortfolioManagerAgent

__all__ = [
    'BaseAgent',
    'SignalGeneratorAgent',
    'RiskManagerAgent',
    'PortfolioManagerAgent'
]
