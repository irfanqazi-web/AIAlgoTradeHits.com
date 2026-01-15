"""
Base Agent Class for Multi-Agent Trading System
All specialized agents inherit from this base class
"""

import uuid
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from google.cloud import bigquery

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent operational states"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    COMPLETED = "completed"


class AgentPriority(Enum):
    """Agent message/task priorities"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AgentMessage:
    """Message structure for inter-agent communication"""

    def __init__(
        self,
        sender: str,
        recipient: str,
        message_type: str,
        payload: Dict[str, Any],
        priority: AgentPriority = AgentPriority.MEDIUM
    ):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.payload = payload
        self.priority = priority
        self.timestamp = datetime.utcnow()
        self.processed = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'sender': self.sender,
            'recipient': self.recipient,
            'message_type': self.message_type,
            'payload': self.payload,
            'priority': self.priority.value,
            'timestamp': self.timestamp.isoformat(),
            'processed': self.processed
        }


class BaseAgent(ABC):
    """
    Base class for all trading agents.
    Provides core functionality for state management, communication, and data access.
    """

    PROJECT_ID = "aialgotradehits"
    DATASET_ID = "crypto_trading_data"

    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: str = "BaseAgent",
        description: str = "",
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id or str(uuid.uuid4())[:8]
        self.name = name
        self.description = description
        self.config = config or {}
        self.state = AgentState.IDLE
        self.created_at = datetime.utcnow()
        self.last_run = None
        self.message_queue: List[AgentMessage] = []
        self.execution_log: List[Dict[str, Any]] = []
        self._bq_client = None

        logger.info(f"Agent initialized: {self.name} ({self.agent_id})")

    @property
    def bq_client(self) -> bigquery.Client:
        """Lazy initialization of BigQuery client"""
        if self._bq_client is None:
            self._bq_client = bigquery.Client(project=self.PROJECT_ID)
        return self._bq_client

    def query_bigquery(self, query: str) -> List[Dict[str, Any]]:
        """Execute a BigQuery query and return results as list of dicts"""
        try:
            results = list(self.bq_client.query(query).result())
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"BigQuery error: {e}")
            return []

    def get_market_data(
        self,
        symbol: str,
        asset_type: str = "stocks",
        timeframe: str = "daily",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch market data for a symbol"""
        table_map = {
            ("stocks", "daily"): "v2_stocks_daily",
            ("stocks", "hourly"): "v2_stocks_hourly",
            ("crypto", "daily"): "v2_crypto_daily",
            ("crypto", "hourly"): "v2_crypto_hourly",
            ("etfs", "daily"): "v2_etfs_daily",
            ("forex", "daily"): "v2_forex_daily",
        }

        table = table_map.get((asset_type, timeframe), f"v2_{asset_type}_{timeframe}")

        query = f"""
        SELECT *
        FROM `{self.PROJECT_ID}.{self.DATASET_ID}.{table}`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        LIMIT {limit}
        """

        return self.query_bigquery(query)

    def receive_message(self, message: AgentMessage):
        """Receive a message from another agent"""
        self.message_queue.append(message)
        logger.info(f"{self.name} received message from {message.sender}: {message.message_type}")

    def send_message(
        self,
        recipient: str,
        message_type: str,
        payload: Dict[str, Any],
        priority: AgentPriority = AgentPriority.MEDIUM
    ) -> AgentMessage:
        """Create a message to send to another agent"""
        message = AgentMessage(
            sender=self.agent_id,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
            priority=priority
        )
        logger.info(f"{self.name} sending message to {recipient}: {message_type}")
        return message

    def process_messages(self) -> List[Dict[str, Any]]:
        """Process all pending messages in the queue"""
        results = []
        # Sort by priority (highest first)
        self.message_queue.sort(key=lambda m: m.priority.value, reverse=True)

        for message in self.message_queue:
            if not message.processed:
                result = self.handle_message(message)
                message.processed = True
                results.append({
                    'message_id': message.id,
                    'type': message.message_type,
                    'result': result
                })

        # Clear processed messages
        self.message_queue = [m for m in self.message_queue if not m.processed]
        return results

    def handle_message(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle a specific message - override in subclasses"""
        return {'status': 'received', 'message_type': message.message_type}

    def log_execution(self, action: str, details: Dict[str, Any]):
        """Log an agent execution action"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'agent_id': self.agent_id,
            'agent_name': self.name,
            'action': action,
            'details': details
        }
        self.execution_log.append(log_entry)
        logger.info(f"{self.name} executed: {action}")

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'description': self.description,
            'state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'pending_messages': len(self.message_queue),
            'execution_count': len(self.execution_log)
        }

    @abstractmethod
    def execute(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main execution method - must be implemented by subclasses
        Returns execution results
        """
        pass

    def run(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run the agent with state management"""
        try:
            self.state = AgentState.RUNNING
            self.last_run = datetime.utcnow()

            # Process any pending messages first
            message_results = self.process_messages()

            # Execute main agent logic
            result = self.execute(context)

            self.state = AgentState.COMPLETED
            self.log_execution('run_completed', {'result': result})

            return {
                'success': True,
                'agent_id': self.agent_id,
                'result': result,
                'message_results': message_results,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.state = AgentState.ERROR
            error_msg = str(e)
            self.log_execution('run_error', {'error': error_msg})
            logger.error(f"{self.name} error: {error_msg}")

            return {
                'success': False,
                'agent_id': self.agent_id,
                'error': error_msg,
                'timestamp': datetime.utcnow().isoformat()
            }
