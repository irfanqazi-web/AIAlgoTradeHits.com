"""
Test Script for AIAlgoTradeHits.com Agentic AI Framework
Verifies all components work correctly before deployment
"""

import os
import sys
import asyncio
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test imports
def test_imports():
    """Test that all modules can be imported"""
    print("\n=== Testing Imports ===")
    try:
        from shared_ai_modules import (
            BaseAgent, AgentConfig,
            AgentMemory,
            ToolRegistry, TradingTools,
            AgentOrchestrator,
            AgentEvaluator
        )
        print("[PASS] All modules imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        return False


def test_memory_system():
    """Test the multi-layer memory system"""
    print("\n=== Testing Memory System ===")
    try:
        from shared_ai_modules.memory import AgentMemory, MemoryEntry

        # Create memory instance
        memory = AgentMemory(user_id="test_user", project="trading")

        # Test episodic memory
        memory.add_conversation("user", "What's the Growth Score for AAPL?")
        memory.add_conversation("assistant", "Let me calculate the Growth Score for AAPL...")

        assert len(memory.conversation_history) == 2
        print("[PASS] Episodic memory working")

        # Test working memory
        memory.update_working_memory("current_symbol", "AAPL")
        memory.update_working_memory("task", "growth_score_calculation")

        assert memory.get_working_memory("current_symbol") == "AAPL"
        print("[PASS] Working memory working")

        # Test insight storage
        memory.store_insight(
            "AAPL showed strong bullish momentum with RSI at 65",
            category="trading_signal",
            metadata={"symbol": "AAPL", "score": 75}
        )

        assert len(memory.insights_cache) == 1
        print("[PASS] Insight storage working")

        # Test context compilation
        context = memory.get_context_for_llm()
        assert "recent_conversation" in context
        assert "current_task" in context
        print("[PASS] Context compilation working")

        # Test export/import
        exported = memory.export_session()
        assert exported["user_id"] == "test_user"
        print("[PASS] Session export working")

        print("[PASS] Memory system tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Memory test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_registry():
    """Test tool registration and execution"""
    print("\n=== Testing Tool Registry ===")
    try:
        from shared_ai_modules.tools import ToolRegistry, TradingTools

        # Test registry
        registry = ToolRegistry()

        # Register a simple test tool
        registry.register(
            "test_tool",
            {
                "name": "test_tool",
                "description": "A test tool",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"}
                    }
                }
            },
            lambda x: {"result": x.get("value", "default")}
        )

        # Test execution
        result = registry.execute("test_tool", {"value": "test123"})
        assert result["result"] == "test123"
        print("[PASS] Tool registration and execution working")

        # Test TradingTools definitions
        tools = TradingTools()
        definitions = TradingTools.get_tool_definitions()

        assert len(definitions) >= 7
        tool_names = [t["name"] for t in definitions]
        assert "get_market_data" in tool_names
        assert "calculate_growth_score" in tool_names
        assert "detect_rise_cycle" in tool_names
        print(f"[PASS] TradingTools has {len(definitions)} tool definitions")

        print("[PASS] Tool registry tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Tool registry test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_orchestrator():
    """Test the agent orchestrator"""
    print("\n=== Testing Orchestrator ===")
    try:
        from shared_ai_modules.orchestrator import (
            AgentOrchestrator, TradingOrchestrator,
            TaskStatus, WorkflowStep
        )

        # Create orchestrator
        orchestrator = AgentOrchestrator()

        # Test workflow definition
        orchestrator.define_workflow("test_workflow", [
            {"agent": "scanner", "action": "scan", "params": {}},
            {"agent": "analyzer", "action": "analyze", "params": {}}
        ])

        assert "test_workflow" in orchestrator.workflows
        print("[PASS] Workflow definition working")

        # Test TradingOrchestrator pre-defined workflows
        trading_orch = TradingOrchestrator()

        assert "full_analysis" in trading_orch.workflows
        assert "quick_screen" in trading_orch.workflows
        assert "rise_cycle_detection" in trading_orch.workflows
        assert "portfolio_review" in trading_orch.workflows
        print("[PASS] TradingOrchestrator has pre-defined workflows")

        # Test stats
        stats = orchestrator.get_workflow_stats()
        assert "message" in stats or "total_executions" in stats
        print("[PASS] Workflow stats working")

        print("[PASS] Orchestrator tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Orchestrator test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_evaluator():
    """Test the agent evaluator"""
    print("\n=== Testing Evaluator ===")
    try:
        from shared_ai_modules.evaluator import (
            AgentEvaluator, TradingAgentEvaluator,
            InteractionMetrics
        )

        # Create evaluator
        evaluator = AgentEvaluator(agent_name="TestAgent")

        # Log some interactions
        evaluator.log_interaction(
            response_time=1.5,
            tool_calls=2,
            tokens_used=500,
            success=True
        )

        evaluator.log_interaction(
            response_time=2.0,
            tool_calls=3,
            tokens_used=750,
            success=True
        )

        evaluator.log_interaction(
            response_time=5.0,
            tool_calls=1,
            tokens_used=300,
            success=False,
            error="Test error"
        )

        assert len(evaluator.metrics_history) == 3
        assert len(evaluator.error_log) == 1
        print("[PASS] Interaction logging working")

        # Test performance analysis
        perf = evaluator.analyze_performance()
        assert perf["total_interactions"] == 3
        assert perf["success_rate"] == 2/3
        print(f"[PASS] Performance analysis: {perf['success_rate']:.1%} success rate")

        # Test error analysis
        errors = evaluator.get_error_analysis()
        assert errors["total_errors"] == 1
        print("[PASS] Error analysis working")

        # Test report generation
        report = evaluator.generate_report(days=7)
        assert report.total_interactions == 3
        print("[PASS] Report generation working")

        # Test TradingAgentEvaluator
        trading_eval = TradingAgentEvaluator()
        trading_eval.log_signal(
            symbol="AAPL",
            signal="BUY",
            growth_score=85,
            price_at_signal=150.50
        )

        assert len(trading_eval.signal_history) == 1
        print("[PASS] Trading signal logging working")

        print("[PASS] Evaluator tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Evaluator test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_agent():
    """Test the base agent class (without API calls)"""
    print("\n=== Testing Base Agent ===")
    try:
        from shared_ai_modules.base_agent import BaseAgent, AgentConfig

        # Create config
        config = AgentConfig(
            name="TestAgent",
            model="claude-sonnet-4-5-20250929",
            temperature=0.3,
            max_tokens=1024,
            system_prompt="You are a test agent.",
            tools=[]
        )

        assert config.name == "TestAgent"
        assert config.tools == []
        print("[PASS] AgentConfig working")

        # Note: We don't test actual API calls here to avoid costs
        # The TradingAgent import requires API key
        print("[INFO] Skipping API-dependent tests (no API key required for framework test)")

        print("[PASS] Base agent tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Base agent test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all framework tests"""
    print("=" * 60)
    print("AIAlgoTradeHits.com Agentic AI Framework Test Suite")
    print("=" * 60)
    print(f"Test Time: {datetime.now().isoformat()}")

    results = {
        "imports": test_imports(),
        "memory": test_memory_system(),
        "tools": test_tool_registry(),
        "orchestrator": test_orchestrator(),
        "evaluator": test_evaluator(),
        "base_agent": test_base_agent()
    }

    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: [{status}]")

    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n[SUCCESS] All framework tests passed!")
        print("The Agentic AI framework is ready for deployment.")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please review errors above.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
