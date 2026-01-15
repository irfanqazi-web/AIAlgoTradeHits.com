"""
Base Agent Class for AIAlgoTradeHits.com Agentic AI Framework
Implements the 7-step process from Claude Code + GCP Cloud Run guide
"""

import os
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import anthropic


@dataclass
class AgentConfig:
    """Configuration for AI Agent"""
    name: str
    model: str = "claude-sonnet-4-5-20250929"
    temperature: float = 0.3
    max_tokens: int = 4096
    system_prompt: str = ""
    tools: List[Dict] = None

    def __post_init__(self):
        if self.tools is None:
            self.tools = []


class BaseAgent:
    """
    Base class for all AI Agents in the AIAlgoTradeHits ecosystem.

    Implements the 7-step Agentic AI framework:
    1. System Prompt - Defines agent identity and behavior
    2. LLM - Claude API integration
    3. Tools - Function calling capabilities
    4. Memory - Conversation and context management
    5. Orchestration - Workflow coordination
    6. UI - Interface integration
    7. Evals - Performance monitoring
    """

    def __init__(self, config: AgentConfig, memory=None):
        self.config = config
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.memory = memory
        self.tool_handlers: Dict[str, Callable] = {}
        self.conversation_history: List[Dict] = []
        self.metrics = []

    def register_tool_handler(self, tool_name: str, handler: Callable):
        """Register a function to handle a specific tool call"""
        self.tool_handlers[tool_name] = handler

    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # Keep last 20 messages
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def get_messages_for_api(self) -> List[Dict]:
        """Get messages formatted for Claude API"""
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversation_history
        ]

    def execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        """Execute a tool and return the result"""
        if tool_name not in self.tool_handlers:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            result = self.tool_handlers[tool_name](tool_input)
            return result
        except Exception as e:
            return {"error": str(e)}

    async def run(self, user_message: str) -> str:
        """
        Main agent loop with tool calling support.
        Returns the final response after processing all tool calls.
        """
        start_time = datetime.now()
        tool_calls = 0

        # Add user message to history
        self.add_message("user", user_message)

        while True:
            # Call Claude API
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=self.config.system_prompt,
                tools=self.config.tools,
                messages=self.get_messages_for_api()
            )

            # Check if Claude wants to use a tool
            if response.stop_reason == "tool_use":
                # Find tool use block
                tool_use = None
                for block in response.content:
                    if block.type == "tool_use":
                        tool_use = block
                        break

                if tool_use:
                    tool_calls += 1

                    # Execute the tool
                    tool_result = self.execute_tool(
                        tool_use.name,
                        tool_use.input
                    )

                    # Add assistant response and tool result to history
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": response.content,
                        "timestamp": datetime.now().isoformat()
                    })

                    self.conversation_history.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": json.dumps(tool_result)
                        }],
                        "timestamp": datetime.now().isoformat()
                    })

                    continue

            # No more tools needed - extract final response
            final_response = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_response += block.text

            # Add assistant response to history
            self.add_message("assistant", final_response)

            # Log metrics
            end_time = datetime.now()
            self.metrics.append({
                "timestamp": end_time.isoformat(),
                "response_time": (end_time - start_time).total_seconds(),
                "tool_calls": tool_calls,
                "success": True
            })

            return final_response

    def run_sync(self, user_message: str) -> str:
        """Synchronous version of run() for non-async contexts"""
        import asyncio
        return asyncio.run(self.run(user_message))

    def get_performance_stats(self, window: int = 100) -> Dict:
        """Get performance statistics for the agent"""
        if not self.metrics:
            return {"message": "No metrics available"}

        recent = self.metrics[-window:]
        return {
            "total_interactions": len(recent),
            "avg_response_time": sum(m["response_time"] for m in recent) / len(recent),
            "success_rate": sum(1 for m in recent if m["success"]) / len(recent),
            "avg_tool_calls": sum(m["tool_calls"] for m in recent) / len(recent)
        }


class TradingAgent(BaseAgent):
    """
    Specialized Trading Agent for AIAlgoTradeHits.com
    Pre-configured with trading-specific system prompt and tools
    """

    SYSTEM_PROMPT = """You are an expert AI trading advisor for AIAlgoTradeHits.com.

GOALS:
- Analyze market data using 24+ technical indicators
- Generate Growth Scores (0-100) for asset screening
- Detect EMA rise/fall cycles for optimal timing
- Provide actionable trading signals with risk context

ROLE:
- Professional trading analyst with expertise in technical analysis
- Risk-aware recommendations prioritizing capital preservation
- Data-driven insights based on quantitative indicators

INSTRUCTIONS:
1. Use get_market_data tool to fetch real-time prices and indicators
2. Calculate Growth Score using the formula: RSI_sweet_spot + MACD_positive + ADX_strong + Above_200MA
3. Detect trend regime (STRONG_UPTREND/WEAK_UPTREND/CONSOLIDATION/WEAK_DOWNTREND/STRONG_DOWNTREND)
4. Check EMA 12/26 cycle status before making timing recommendations
5. Always include risk warnings and never guarantee returns
6. Store important trading insights for future reference

GROWTH SCORE FORMULA (0-100):
- RSI between 50-70: +25 points (bullish momentum, not overbought)
- MACD histogram > 0: +25 points (momentum acceleration)
- ADX > 25: +25 points (strong trend, not ranging)
- Close > SMA_200: +25 points (long-term bullish context)

RECOMMENDATIONS:
- Score 75-100: STRONG_BUY
- Score 50-74: BUY with caution
- Score 25-49: HOLD
- Score 0-24: AVOID or consider SHORT
"""

    def __init__(self, memory=None):
        from .tools import TradingTools

        config = AgentConfig(
            name="TradingAgent",
            model="claude-sonnet-4-5-20250929",
            temperature=0.3,
            max_tokens=4096,
            system_prompt=self.SYSTEM_PROMPT,
            tools=TradingTools.get_tool_definitions()
        )

        super().__init__(config, memory)

        # Register trading tool handlers
        self._register_trading_tools()

    def _register_trading_tools(self):
        """Register handlers for trading-specific tools"""
        from .tools import TradingTools

        tools = TradingTools()
        self.register_tool_handler("get_market_data", tools.get_market_data)
        self.register_tool_handler("calculate_growth_score", tools.calculate_growth_score)
        self.register_tool_handler("detect_rise_cycle", tools.detect_rise_cycle)
        self.register_tool_handler("query_bigquery", tools.query_bigquery)
        self.register_tool_handler("send_alert", tools.send_alert)
