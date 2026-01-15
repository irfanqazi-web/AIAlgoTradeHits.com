"""
MarketingAI Backend Package
AI-powered marketing automation with Google Vertex AI
"""

# Import AI module getters for easy access
from .ai_gemini import get_gemini_generator
from .ai_imagen import get_imagen_generator
from .ai_veo import get_veo_generator
from .ai_lyria import get_lyria_generator
from .ai_agents import (
    get_marketing_orchestrator,
    Task,
    TaskStatus,
    AgentType,
    WorkflowPattern,
    WorkflowContext
)

__all__ = [
    # Generators
    'get_gemini_generator',
    'get_imagen_generator',
    'get_veo_generator',
    'get_lyria_generator',
    'get_marketing_orchestrator',
    # Agent classes
    'Task',
    'TaskStatus',
    'AgentType',
    'WorkflowPattern',
    'WorkflowContext'
]

__version__ = '2.0.0'
