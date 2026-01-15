"""
Agent Evaluator for AIAlgoTradeHits.com
Monitors and evaluates AI agent performance
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json


@dataclass
class InteractionMetrics:
    """Metrics for a single agent interaction"""
    timestamp: str
    response_time: float
    tool_calls: int
    tokens_used: int
    success: bool
    error: Optional[str] = None
    user_satisfaction: Optional[float] = None
    agent_name: str = ""


@dataclass
class EvaluationReport:
    """Comprehensive evaluation report"""
    period_start: str
    period_end: str
    total_interactions: int
    success_rate: float
    avg_response_time: float
    avg_tool_calls: float
    error_rate: float
    top_errors: List[Dict]
    recommendations: List[str]


class AgentEvaluator:
    """
    Evaluates and monitors AI agent performance.

    Tracks:
    - Response times
    - Success/failure rates
    - Tool usage patterns
    - Error frequency and types
    - User satisfaction (when available)
    """

    def __init__(self, agent_name: str = "default"):
        self.agent_name = agent_name
        self.metrics_history: List[InteractionMetrics] = []
        self.error_log: List[Dict] = []
        self._bigquery = None

    @property
    def bigquery(self):
        """Lazy-load BigQuery client for persistent metrics storage"""
        if self._bigquery is None:
            try:
                from google.cloud import bigquery
                self._bigquery = bigquery.Client(
                    project=os.getenv("GCP_PROJECT_ID", "aialgotradehits")
                )
            except Exception:
                pass
        return self._bigquery

    def log_interaction(
        self,
        response_time: float,
        tool_calls: int,
        tokens_used: int,
        success: bool,
        error: str = None,
        user_satisfaction: float = None
    ):
        """Log metrics for a single interaction"""
        metrics = InteractionMetrics(
            timestamp=datetime.now().isoformat(),
            response_time=response_time,
            tool_calls=tool_calls,
            tokens_used=tokens_used,
            success=success,
            error=error,
            user_satisfaction=user_satisfaction,
            agent_name=self.agent_name
        )

        self.metrics_history.append(metrics)

        # Log errors separately for analysis
        if error:
            self.error_log.append({
                "timestamp": metrics.timestamp,
                "error": error,
                "agent_name": self.agent_name
            })

        # Persist to BigQuery if available
        self._persist_metrics(metrics)

    def _persist_metrics(self, metrics: InteractionMetrics):
        """Persist metrics to BigQuery"""
        if not self.bigquery:
            return

        try:
            table_id = "aialgotradehits.ml_models.agent_metrics"
            rows = [{
                "timestamp": metrics.timestamp,
                "agent_name": metrics.agent_name,
                "response_time": metrics.response_time,
                "tool_calls": metrics.tool_calls,
                "tokens_used": metrics.tokens_used,
                "success": metrics.success,
                "error": metrics.error,
                "user_satisfaction": metrics.user_satisfaction
            }]

            errors = self.bigquery.insert_rows_json(table_id, rows)
            if errors:
                print(f"Failed to persist metrics: {errors}")

        except Exception as e:
            # Silently fail - don't break the agent for metrics
            pass

    def analyze_performance(self, window: int = 100) -> Dict:
        """Analyze recent performance metrics"""
        if not self.metrics_history:
            return {"message": "No metrics available"}

        recent = self.metrics_history[-window:]

        # Calculate statistics
        success_count = sum(1 for m in recent if m.success)
        total_response_time = sum(m.response_time for m in recent)
        total_tool_calls = sum(m.tool_calls for m in recent)
        total_tokens = sum(m.tokens_used for m in recent)

        # User satisfaction (where available)
        satisfaction_scores = [m.user_satisfaction for m in recent if m.user_satisfaction is not None]

        return {
            "period": f"Last {len(recent)} interactions",
            "total_interactions": len(recent),
            "success_rate": success_count / len(recent) if recent else 0,
            "avg_response_time": total_response_time / len(recent) if recent else 0,
            "avg_tool_calls": total_tool_calls / len(recent) if recent else 0,
            "avg_tokens_used": total_tokens / len(recent) if recent else 0,
            "avg_user_satisfaction": sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else None,
            "error_rate": (len(recent) - success_count) / len(recent) if recent else 0
        }

    def get_error_analysis(self) -> Dict:
        """Analyze error patterns"""
        if not self.error_log:
            return {"message": "No errors logged"}

        # Group errors by type
        error_types = {}
        for entry in self.error_log:
            error = entry["error"]
            # Extract error type (first line or first 50 chars)
            error_type = error.split('\n')[0][:50] if error else "Unknown"

            if error_type not in error_types:
                error_types[error_type] = {"count": 0, "examples": []}

            error_types[error_type]["count"] += 1
            if len(error_types[error_type]["examples"]) < 3:
                error_types[error_type]["examples"].append({
                    "timestamp": entry["timestamp"],
                    "full_error": error
                })

        # Sort by frequency
        sorted_errors = sorted(
            error_types.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )

        return {
            "total_errors": len(self.error_log),
            "unique_error_types": len(error_types),
            "top_errors": [
                {"type": k, "count": v["count"], "examples": v["examples"]}
                for k, v in sorted_errors[:10]
            ]
        }

    def generate_report(self, days: int = 7) -> EvaluationReport:
        """Generate comprehensive evaluation report"""
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        # Filter metrics for the period
        period_metrics = [
            m for m in self.metrics_history
            if m.timestamp >= cutoff_str
        ]

        if not period_metrics:
            return EvaluationReport(
                period_start=cutoff_str,
                period_end=datetime.now().isoformat(),
                total_interactions=0,
                success_rate=0,
                avg_response_time=0,
                avg_tool_calls=0,
                error_rate=0,
                top_errors=[],
                recommendations=["No data available for this period"]
            )

        # Calculate metrics
        total = len(period_metrics)
        successes = sum(1 for m in period_metrics if m.success)
        total_time = sum(m.response_time for m in period_metrics)
        total_tools = sum(m.tool_calls for m in period_metrics)

        # Get top errors
        period_errors = [
            e for e in self.error_log
            if e["timestamp"] >= cutoff_str
        ]

        error_types = {}
        for e in period_errors:
            error_type = e["error"][:50] if e["error"] else "Unknown"
            error_types[error_type] = error_types.get(error_type, 0) + 1

        top_errors = [
            {"error": k, "count": v}
            for k, v in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        # Generate recommendations
        recommendations = self._generate_recommendations(
            success_rate=successes / total,
            avg_response_time=total_time / total,
            error_rate=(total - successes) / total,
            top_errors=top_errors
        )

        return EvaluationReport(
            period_start=cutoff_str,
            period_end=datetime.now().isoformat(),
            total_interactions=total,
            success_rate=successes / total,
            avg_response_time=total_time / total,
            avg_tool_calls=total_tools / total,
            error_rate=(total - successes) / total,
            top_errors=top_errors,
            recommendations=recommendations
        )

    def _generate_recommendations(
        self,
        success_rate: float,
        avg_response_time: float,
        error_rate: float,
        top_errors: List[Dict]
    ) -> List[str]:
        """Generate actionable recommendations based on metrics"""
        recommendations = []

        # Success rate recommendations
        if success_rate < 0.95:
            recommendations.append(
                f"Success rate ({success_rate:.1%}) is below target (95%). "
                "Review error logs and implement error handling improvements."
            )

        # Response time recommendations
        if avg_response_time > 5.0:
            recommendations.append(
                f"Average response time ({avg_response_time:.1f}s) is slow. "
                "Consider optimizing tool calls or caching frequent queries."
            )

        # Error pattern recommendations
        if top_errors:
            most_common = top_errors[0]
            recommendations.append(
                f"Most common error: '{most_common['error']}' ({most_common['count']} occurrences). "
                "Prioritize fixing this error pattern."
            )

        # Add positive feedback if metrics are good
        if success_rate >= 0.98 and avg_response_time < 2.0:
            recommendations.append(
                "Agent performance is excellent! Consider expanding capabilities."
            )

        if not recommendations:
            recommendations.append("Agent performance is within acceptable parameters.")

        return recommendations

    def export_metrics(self, filepath: str = None) -> str:
        """Export metrics to JSON file"""
        data = {
            "agent_name": self.agent_name,
            "exported_at": datetime.now().isoformat(),
            "metrics": [
                {
                    "timestamp": m.timestamp,
                    "response_time": m.response_time,
                    "tool_calls": m.tool_calls,
                    "tokens_used": m.tokens_used,
                    "success": m.success,
                    "error": m.error
                }
                for m in self.metrics_history
            ],
            "error_log": self.error_log,
            "summary": self.analyze_performance()
        }

        if filepath:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return filepath

        return json.dumps(data, indent=2)

    def clear_metrics(self):
        """Clear all stored metrics (use with caution)"""
        self.metrics_history = []
        self.error_log = []


class TradingAgentEvaluator(AgentEvaluator):
    """
    Specialized evaluator for trading agents.
    Tracks trading-specific metrics like signal accuracy.
    """

    def __init__(self):
        super().__init__(agent_name="TradingAgent")
        self.signal_history: List[Dict] = []

    def log_signal(
        self,
        symbol: str,
        signal: str,
        growth_score: int,
        price_at_signal: float
    ):
        """Log a trading signal for later evaluation"""
        self.signal_history.append({
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "signal": signal,
            "growth_score": growth_score,
            "price_at_signal": price_at_signal,
            "outcome": None,  # Will be updated later
            "actual_return": None
        })

    def evaluate_signal_accuracy(self, days: int = 30) -> Dict:
        """Evaluate accuracy of trading signals"""
        if not self.signal_history:
            return {"message": "No signals to evaluate"}

        # In production, this would fetch actual price data
        # and compare against signal predictions

        signals_by_type = {}
        for signal in self.signal_history:
            signal_type = signal["signal"]
            if signal_type not in signals_by_type:
                signals_by_type[signal_type] = {"count": 0, "correct": 0}
            signals_by_type[signal_type]["count"] += 1

        return {
            "total_signals": len(self.signal_history),
            "signals_by_type": signals_by_type,
            "evaluation_period": f"Last {days} days"
        }
