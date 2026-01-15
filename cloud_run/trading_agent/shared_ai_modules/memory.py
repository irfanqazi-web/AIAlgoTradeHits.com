"""
Agent Memory System for AIAlgoTradeHits.com
Multi-layer memory: Episodic, Working, Long-term (BigQuery/Firestore)
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class MemoryEntry:
    """Single memory entry"""
    content: str
    category: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


class AgentMemory:
    """
    Multi-layer memory system for AI agents.

    Layers:
    1. Episodic - Conversation history (short-term)
    2. Working - Current task context
    3. Long-term - Persistent storage (BigQuery/Firestore)
    """

    def __init__(self, user_id: str, project: str = "trading"):
        self.user_id = user_id
        self.project = project

        # Episodic memory (conversation history)
        self.conversation_history: List[Dict] = []

        # Working memory (current task context)
        self.working_memory: Dict[str, Any] = {}

        # Long-term memory (lazy-loaded)
        self._firestore = None
        self._bigquery = None

        # Local cache for insights
        self.insights_cache: List[MemoryEntry] = []

    @property
    def firestore(self):
        """Lazy-load Firestore client"""
        if self._firestore is None:
            try:
                from google.cloud import firestore
                self._firestore = firestore.Client(
                    project=os.getenv("GCP_PROJECT_ID", "aialgotradehits")
                )
            except Exception as e:
                print(f"Firestore not available: {e}")
        return self._firestore

    @property
    def bigquery(self):
        """Lazy-load BigQuery client"""
        if self._bigquery is None:
            try:
                from google.cloud import bigquery
                self._bigquery = bigquery.Client(
                    project=os.getenv("GCP_PROJECT_ID", "aialgotradehits")
                )
            except Exception as e:
                print(f"BigQuery not available: {e}")
        return self._bigquery

    def add_conversation(self, role: str, content: str):
        """Add message to episodic memory"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(message)

        # Keep only last 20 messages
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def get_conversation(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:]

    def update_working_memory(self, key: str, value: Any):
        """Update working memory for current task"""
        self.working_memory[key] = {
            "value": value,
            "updated_at": datetime.now().isoformat()
        }

    def get_working_memory(self, key: str = None) -> Any:
        """Get working memory value or entire working memory"""
        if key:
            entry = self.working_memory.get(key)
            return entry["value"] if entry else None
        return self.working_memory

    def clear_working_memory(self):
        """Clear working memory for new task"""
        self.working_memory = {}

    def store_insight(self, insight: str, category: str, metadata: Dict = None):
        """Store important insight in long-term memory"""
        entry = MemoryEntry(
            content=insight,
            category=category,
            metadata=metadata or {}
        )

        # Add to local cache
        self.insights_cache.append(entry)

        # Store in Firestore if available
        if self.firestore:
            try:
                from google.cloud import firestore as fs
                self.firestore.collection(f'{self.project}_insights').add({
                    'user_id': self.user_id,
                    'insight': insight,
                    'category': category,
                    'metadata': metadata or {},
                    'timestamp': fs.SERVER_TIMESTAMP
                })
            except Exception as e:
                print(f"Failed to store insight in Firestore: {e}")

    def search_insights(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Search insights by keyword (simple implementation)"""
        query_lower = query.lower()
        results = [
            entry for entry in self.insights_cache
            if query_lower in entry.content.lower() or query_lower in entry.category.lower()
        ]
        return results[:limit]

    def get_user_preferences(self) -> Dict:
        """Retrieve user preferences from Firestore"""
        if not self.firestore:
            return {}

        try:
            doc = self.firestore.collection('users').document(self.user_id).get()
            return doc.to_dict() if doc.exists else {}
        except Exception as e:
            print(f"Failed to get user preferences: {e}")
            return {}

    def save_user_preference(self, key: str, value: Any):
        """Save user preference to Firestore"""
        if not self.firestore:
            return

        try:
            self.firestore.collection('users').document(self.user_id).set(
                {key: value},
                merge=True
            )
        except Exception as e:
            print(f"Failed to save user preference: {e}")

    def get_context_for_llm(self) -> Dict:
        """
        Compile all relevant memory context for LLM call.
        This is what gets passed to the agent for context-aware responses.
        """
        return {
            "recent_conversation": self.get_conversation(10),
            "current_task": self.working_memory,
            "user_preferences": self.get_user_preferences(),
            "recent_insights": [
                {"content": e.content, "category": e.category}
                for e in self.insights_cache[-5:]
            ]
        }

    def export_session(self) -> Dict:
        """Export current session data for persistence"""
        return {
            "user_id": self.user_id,
            "project": self.project,
            "conversation_history": self.conversation_history,
            "working_memory": self.working_memory,
            "insights": [
                {
                    "content": e.content,
                    "category": e.category,
                    "timestamp": e.timestamp,
                    "metadata": e.metadata
                }
                for e in self.insights_cache
            ],
            "exported_at": datetime.now().isoformat()
        }

    def import_session(self, data: Dict):
        """Import session data from previous export"""
        self.conversation_history = data.get("conversation_history", [])
        self.working_memory = data.get("working_memory", {})

        for insight in data.get("insights", []):
            self.insights_cache.append(MemoryEntry(
                content=insight["content"],
                category=insight["category"],
                timestamp=insight.get("timestamp", datetime.now().isoformat()),
                metadata=insight.get("metadata", {})
            ))
