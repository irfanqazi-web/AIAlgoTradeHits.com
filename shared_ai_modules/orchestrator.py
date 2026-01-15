"""
Agent Orchestrator for AIAlgoTradeHits.com
Coordinates multiple agents and workflows
"""

import asyncio
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowStep:
    """Single step in a workflow"""
    agent: str
    action: str
    params: Dict = field(default_factory=dict)
    depends_on: Optional[str] = None


@dataclass
class WorkflowResult:
    """Result of workflow execution"""
    status: TaskStatus
    results: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    context: Dict = field(default_factory=dict)
    execution_time: float = 0.0


class AgentOrchestrator:
    """
    Orchestrates multiple AI agents and workflows.

    Features:
    - Agent registration and management
    - Workflow definition and execution
    - Agent-to-agent communication
    - Error handling and recovery
    """

    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.workflows: Dict[str, List[WorkflowStep]] = {}
        self.execution_history: List[Dict] = []

    def register_agent(self, name: str, agent_instance):
        """Register an agent for use in workflows"""
        self.agents[name] = agent_instance
        print(f"Registered agent: {name}")

    def unregister_agent(self, name: str):
        """Remove an agent from the registry"""
        if name in self.agents:
            del self.agents[name]
            print(f"Unregistered agent: {name}")

    def define_workflow(self, name: str, steps: List[Dict]):
        """
        Define a workflow as a sequence of steps.

        Example:
        steps = [
            {"agent": "scanner", "action": "scan_markets", "params": {}},
            {"agent": "analyst", "action": "analyze", "params": {}},
            {"agent": "reporter", "action": "generate_report", "params": {}}
        ]
        """
        workflow_steps = [
            WorkflowStep(
                agent=step["agent"],
                action=step["action"],
                params=step.get("params", {}),
                depends_on=step.get("depends_on")
            )
            for step in steps
        ]
        self.workflows[name] = workflow_steps
        print(f"Defined workflow: {name} with {len(workflow_steps)} steps")

    async def execute_workflow(
        self,
        workflow_name: str,
        initial_params: Dict = None
    ) -> WorkflowResult:
        """Execute a defined workflow"""
        start_time = datetime.now()

        if workflow_name not in self.workflows:
            return WorkflowResult(
                status=TaskStatus.FAILED,
                errors=[f"Workflow '{workflow_name}' not found"]
            )

        steps = self.workflows[workflow_name]
        context = initial_params.copy() if initial_params else {}
        results = []
        errors = []

        for i, step in enumerate(steps):
            step_name = f"{step.agent}.{step.action}"
            print(f"Executing step {i+1}/{len(steps)}: {step_name}")

            agent = self.agents.get(step.agent)
            if not agent:
                error_msg = f"Agent '{step.agent}' not found"
                errors.append(error_msg)
                print(f"Error: {error_msg}")
                continue

            # Merge step params with context
            params = {**context, **step.params}

            try:
                # Execute the step
                if hasattr(agent, 'execute'):
                    result = await agent.execute(step.action, params)
                elif hasattr(agent, step.action):
                    method = getattr(agent, step.action)
                    if asyncio.iscoroutinefunction(method):
                        result = await method(params)
                    else:
                        result = method(params)
                else:
                    result = {"error": f"Action '{step.action}' not found on agent"}

                results.append({
                    "step": step_name,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })

                # Update context with result
                context[f"{step.agent}_result"] = result
                context["last_result"] = result

            except Exception as e:
                error_msg = f"Step {step_name} failed: {str(e)}"
                errors.append(error_msg)
                print(f"Error: {error_msg}")

                # Continue to next step or abort based on configuration
                # For now, we continue

        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        # Determine final status
        if errors and not results:
            status = TaskStatus.FAILED
        elif errors:
            status = TaskStatus.COMPLETED  # Partial success
        else:
            status = TaskStatus.COMPLETED

        # Log execution
        self.execution_history.append({
            "workflow": workflow_name,
            "status": status.value,
            "steps_completed": len(results),
            "errors": len(errors),
            "execution_time": execution_time,
            "timestamp": end_time.isoformat()
        })

        return WorkflowResult(
            status=status,
            results=results,
            errors=errors,
            context=context,
            execution_time=execution_time
        )

    async def agent_to_agent_call(
        self,
        from_agent: str,
        to_agent: str,
        message: str,
        params: Dict = None
    ) -> Dict:
        """Enable direct agent-to-agent communication"""
        target_agent = self.agents.get(to_agent)

        if not target_agent:
            return {"error": f"Agent '{to_agent}' not found"}

        print(f"Agent communication: {from_agent} -> {to_agent}")

        try:
            if hasattr(target_agent, 'run'):
                response = await target_agent.run(message)
            elif hasattr(target_agent, 'process_message'):
                response = await target_agent.process_message(message, params or {})
            else:
                response = {"error": "Agent does not support direct messages"}

            return {
                "from": from_agent,
                "to": to_agent,
                "message": message,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}

    def get_execution_history(self, limit: int = 100) -> List[Dict]:
        """Get recent workflow execution history"""
        return self.execution_history[-limit:]

    def get_workflow_stats(self) -> Dict:
        """Get statistics about workflow executions"""
        if not self.execution_history:
            return {"message": "No executions yet"}

        total = len(self.execution_history)
        completed = sum(1 for e in self.execution_history if e["status"] == "completed")
        failed = sum(1 for e in self.execution_history if e["status"] == "failed")
        avg_time = sum(e["execution_time"] for e in self.execution_history) / total

        return {
            "total_executions": total,
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total if total > 0 else 0,
            "avg_execution_time": avg_time
        }


class TradingOrchestrator(AgentOrchestrator):
    """
    Specialized orchestrator for trading workflows.
    Pre-configured with common trading analysis workflows.
    """

    def __init__(self):
        super().__init__()
        self._define_trading_workflows()

    def _define_trading_workflows(self):
        """Define standard trading workflows"""

        # Full market analysis workflow
        self.define_workflow("full_analysis", [
            {"agent": "market_scanner", "action": "scan_markets", "params": {}},
            {"agent": "technical_analyst", "action": "analyze_technicals", "params": {}},
            {"agent": "risk_assessor", "action": "assess_risk", "params": {}},
            {"agent": "signal_generator", "action": "generate_signals", "params": {}}
        ])

        # Quick screening workflow
        self.define_workflow("quick_screen", [
            {"agent": "market_scanner", "action": "quick_scan", "params": {"limit": 20}},
            {"agent": "signal_generator", "action": "rank_opportunities", "params": {}}
        ])

        # Rise cycle detection workflow
        self.define_workflow("rise_cycle_detection", [
            {"agent": "cycle_detector", "action": "detect_cycles", "params": {}},
            {"agent": "technical_analyst", "action": "confirm_signals", "params": {}},
            {"agent": "alert_manager", "action": "send_alerts", "params": {}}
        ])

        # Portfolio review workflow
        self.define_workflow("portfolio_review", [
            {"agent": "portfolio_analyzer", "action": "get_holdings", "params": {}},
            {"agent": "risk_assessor", "action": "assess_portfolio_risk", "params": {}},
            {"agent": "reporter", "action": "generate_report", "params": {}}
        ])

    async def run_morning_analysis(self) -> WorkflowResult:
        """Run the standard morning market analysis"""
        return await self.execute_workflow("full_analysis", {
            "market_hours": "pre-market",
            "focus": ["stocks", "crypto"]
        })

    async def scan_for_opportunities(self, min_score: int = 75) -> WorkflowResult:
        """Scan for high Growth Score opportunities"""
        return await self.execute_workflow("quick_screen", {
            "min_growth_score": min_score,
            "asset_types": ["stocks", "crypto"]
        })

    async def check_rise_cycles(self) -> WorkflowResult:
        """Check for new rise cycle entries"""
        return await self.execute_workflow("rise_cycle_detection", {
            "lookback_days": 7,
            "min_volume_ratio": 1.2
        })
