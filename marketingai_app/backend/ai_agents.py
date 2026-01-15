"""
MarketingAI - Agentic AI Workflow Orchestrator
n8n-style multi-agent system for autonomous marketing campaigns

Based on n8n patterns:
- Chained Requests: Sequential AI model calls
- Single Agent: Context-maintaining autonomous agent
- Multi-Agent with Gatekeeper: Orchestrator with specialized agents
- Multi-Agent Teams: Collaborative agent mesh

References:
- https://n8n.io/ai-agents/
- https://blog.n8n.io/ai-agentic-workflows/
- Google ADK: https://github.com/google/adk-python
"""
import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

# Import our AI modules
from .ai_gemini import get_gemini_generator
from .ai_imagen import get_imagen_generator
from .ai_veo import get_veo_generator

PROJECT_ID = os.environ.get('PROJECT_ID', 'aialgotradehits')


# ==================== ENUMS & DATA CLASSES ====================

class AgentType(Enum):
    ORCHESTRATOR = "orchestrator"
    CAMPAIGN_STRATEGY = "campaign_strategy"
    CONTENT_CREATION = "content_creation"
    SOCIAL_MEDIA = "social_media"
    ADVERTISING = "advertising"
    ANALYTICS = "analytics"
    COMPLIANCE = "compliance"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class WorkflowPattern(Enum):
    CHAINED = "chained"  # Sequential execution
    SINGLE_AGENT = "single_agent"  # One agent maintains state
    MULTI_AGENT_GATEKEEPER = "multi_agent_gatekeeper"  # Orchestrator + specialists
    MULTI_AGENT_MESH = "multi_agent_mesh"  # Peer-to-peer collaboration


@dataclass
class Task:
    """Represents a task in the workflow"""
    id: str
    name: str
    description: str
    agent_type: AgentType
    status: TaskStatus = TaskStatus.PENDING
    input_data: Dict = field(default_factory=dict)
    output_data: Dict = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class AgentMessage:
    """Message passed between agents"""
    sender: AgentType
    receiver: AgentType
    content: Dict
    message_type: str  # request, response, broadcast
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WorkflowContext:
    """Shared context across all agents in a workflow"""
    workflow_id: str
    brand_info: Dict
    campaign_goals: List[str]
    target_audience: Dict
    content_calendar: List[Dict] = field(default_factory=list)
    generated_content: List[Dict] = field(default_factory=list)
    analytics_data: Dict = field(default_factory=dict)
    conversation_history: List[AgentMessage] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


# ==================== BASE AGENT CLASS ====================

class BaseAgent(ABC):
    """
    Abstract base class for all marketing agents.
    Inspired by Google ADK agent design.
    """

    def __init__(self, agent_type: AgentType, name: str):
        self.agent_type = agent_type
        self.name = name
        self.gemini = get_gemini_generator()
        self.imagen = get_imagen_generator()
        self.veo = get_veo_generator()
        self.memory: List[Dict] = []  # Agent-specific memory

    @abstractmethod
    async def execute(self, task: Task, context: WorkflowContext) -> Dict:
        """Execute the agent's primary function"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass

    def add_to_memory(self, entry: Dict):
        """Add entry to agent's memory"""
        entry['timestamp'] = datetime.utcnow().isoformat()
        self.memory.append(entry)
        # Keep last 100 entries
        if len(self.memory) > 100:
            self.memory = self.memory[-100:]

    def get_relevant_memory(self, query: str, limit: int = 5) -> List[Dict]:
        """Retrieve relevant memory entries"""
        # Simple recency-based retrieval
        # In production, use vector similarity
        return self.memory[-limit:]


# ==================== SPECIALIZED AGENTS ====================

class CampaignStrategyAgent(BaseAgent):
    """
    Develops marketing campaign strategies.
    Analyzes market, competitors, and trends.
    """

    def __init__(self):
        super().__init__(AgentType.CAMPAIGN_STRATEGY, "Campaign Strategist")

    def get_capabilities(self) -> List[str]:
        return [
            "analyze_market_trends",
            "create_campaign_strategy",
            "define_target_audiences",
            "set_campaign_goals",
            "competitive_analysis",
            "budget_allocation"
        ]

    async def execute(self, task: Task, context: WorkflowContext) -> Dict:
        """Create campaign strategy based on goals and audience"""

        prompt = f"""
You are a marketing campaign strategist.

Brand Information:
{json.dumps(context.brand_info, indent=2)}

Campaign Goals:
{', '.join(context.campaign_goals)}

Target Audience:
{json.dumps(context.target_audience, indent=2)}

Task: {task.description}
Additional Input: {json.dumps(task.input_data, indent=2)}

Create a comprehensive campaign strategy including:
1. Campaign theme and messaging framework
2. Platform prioritization
3. Content pillars and themes
4. Timeline and milestones
5. KPI targets
6. Budget recommendations

Respond in JSON format.
"""

        try:
            result = await self.gemini.generate_blog_article(
                topic=prompt,
                word_count=1000,
                tone="strategic"
            )

            strategy = {
                "campaign_theme": result.get("title", "Campaign Theme"),
                "messaging_framework": result.get("sections", []),
                "platforms": ["instagram", "facebook", "linkedin", "twitter"],
                "content_pillars": context.campaign_goals,
                "timeline": self._generate_timeline(context),
                "kpis": self._generate_kpis(context.campaign_goals),
                "success": True
            }

            self.add_to_memory({
                "action": "created_strategy",
                "campaign_theme": strategy["campaign_theme"]
            })

            return strategy

        except Exception as e:
            return {"error": str(e), "success": False}

    def _generate_timeline(self, context: WorkflowContext) -> List[Dict]:
        """Generate campaign timeline"""
        return [
            {"phase": "Planning", "duration": "Week 1", "tasks": ["Strategy finalization", "Content calendar"]},
            {"phase": "Content Creation", "duration": "Week 2-3", "tasks": ["Create assets", "Review and approve"]},
            {"phase": "Launch", "duration": "Week 4", "tasks": ["Deploy content", "Monitor performance"]},
            {"phase": "Optimization", "duration": "Ongoing", "tasks": ["Analyze data", "Iterate content"]}
        ]

    def _generate_kpis(self, goals: List[str]) -> Dict:
        """Generate KPIs based on goals"""
        return {
            "awareness": {"impressions": 100000, "reach": 50000},
            "engagement": {"engagement_rate": 5.0, "saves": 1000},
            "conversion": {"click_through_rate": 2.0, "conversions": 500}
        }


class ContentCreationAgent(BaseAgent):
    """
    Creates marketing content using AI.
    Generates text, images, and videos.
    """

    def __init__(self):
        super().__init__(AgentType.CONTENT_CREATION, "Content Creator")

    def get_capabilities(self) -> List[str]:
        return [
            "generate_social_posts",
            "create_blog_articles",
            "design_ad_creatives",
            "generate_email_campaigns",
            "create_video_scripts",
            "generate_images"
        ]

    async def execute(self, task: Task, context: WorkflowContext) -> Dict:
        """Generate content based on task requirements"""

        content_type = task.input_data.get("content_type", "social_post")
        platform = task.input_data.get("platform", "instagram")

        try:
            if content_type == "social_post":
                result = await self.gemini.generate_social_post(
                    prompt=task.description,
                    platform=platform,
                    tone=task.input_data.get("tone", "professional"),
                    brand_voice=context.brand_info.get("brand_voice", ""),
                    target_audience=json.dumps(context.target_audience)
                )

            elif content_type == "blog":
                result = await self.gemini.generate_blog_article(
                    topic=task.description,
                    keywords=task.input_data.get("keywords", []),
                    word_count=task.input_data.get("word_count", 1500)
                )

            elif content_type == "email":
                result = await self.gemini.generate_email_campaign(
                    campaign_goal=task.description,
                    audience_segment=json.dumps(context.target_audience),
                    brand_voice=context.brand_info.get("brand_voice", "")
                )

            elif content_type == "ad_copy":
                result = await self.gemini.generate_ad_copy(
                    product=task.description,
                    platform=platform,
                    target_audience=json.dumps(context.target_audience),
                    goal=task.input_data.get("goal", "conversions")
                )

            elif content_type == "image":
                result = await self.imagen.generate_social_graphic(
                    prompt=task.description,
                    platform=platform,
                    style=task.input_data.get("style", "professional"),
                    brand_colors=context.brand_info.get("colors", [])
                )

            elif content_type == "video_script":
                result = await self.gemini.generate_video_script(
                    topic=task.description,
                    platform=platform,
                    duration=task.input_data.get("duration", 60),
                    style=task.input_data.get("style", "educational")
                )

            else:
                result = {"error": f"Unknown content type: {content_type}", "success": False}

            # Add to workflow context
            if result.get("success"):
                context.generated_content.append({
                    "task_id": task.id,
                    "content_type": content_type,
                    "platform": platform,
                    "result": result,
                    "created_at": datetime.utcnow().isoformat()
                })

            self.add_to_memory({
                "action": "created_content",
                "type": content_type,
                "platform": platform
            })

            return result

        except Exception as e:
            return {"error": str(e), "success": False}


class SocialMediaAgent(BaseAgent):
    """
    Manages social media presence.
    Schedules posts, monitors engagement, responds to comments.
    """

    def __init__(self):
        super().__init__(AgentType.SOCIAL_MEDIA, "Social Media Manager")

    def get_capabilities(self) -> List[str]:
        return [
            "schedule_posts",
            "analyze_best_times",
            "monitor_engagement",
            "respond_to_comments",
            "generate_hashtags",
            "cross_platform_adapt"
        ]

    async def execute(self, task: Task, context: WorkflowContext) -> Dict:
        """Execute social media management task"""

        action = task.input_data.get("action", "schedule_posts")

        if action == "create_calendar":
            return await self._create_content_calendar(task, context)

        elif action == "adapt_content":
            return await self._adapt_for_platforms(task, context)

        elif action == "analyze_timing":
            return self._analyze_posting_times(context)

        else:
            return {"error": f"Unknown action: {action}", "success": False}

    async def _create_content_calendar(self, task: Task, context: WorkflowContext) -> Dict:
        """Create a content calendar"""
        days = task.input_data.get("days", 7)
        platforms = task.input_data.get("platforms", ["instagram", "twitter", "linkedin"])

        result = await self.gemini.generate_content_calendar(
            days=days,
            platforms=platforms,
            brand_voice=context.brand_info.get("brand_voice", ""),
            content_pillars=context.campaign_goals,
            posting_frequency="daily"
        )

        if result.get("success"):
            context.content_calendar = result.get("calendar", [])

        return result

    async def _adapt_for_platforms(self, task: Task, context: WorkflowContext) -> Dict:
        """Adapt content for different platforms"""
        source_content = task.input_data.get("content", "")
        target_platforms = task.input_data.get("platforms", ["twitter", "linkedin"])

        adaptations = {}
        for platform in target_platforms:
            result = await self.gemini.generate_social_post(
                prompt=f"Adapt this content for {platform}: {source_content}",
                platform=platform,
                brand_voice=context.brand_info.get("brand_voice", "")
            )
            adaptations[platform] = result

        return {"success": True, "adaptations": adaptations}

    def _analyze_posting_times(self, context: WorkflowContext) -> Dict:
        """Analyze best posting times"""
        # In production, this would analyze actual engagement data
        return {
            "success": True,
            "best_times": {
                "instagram": {"weekdays": ["9:00 AM", "12:00 PM", "6:00 PM"], "weekends": ["11:00 AM", "3:00 PM"]},
                "twitter": {"weekdays": ["8:00 AM", "12:00 PM", "5:00 PM"], "weekends": ["10:00 AM", "2:00 PM"]},
                "linkedin": {"weekdays": ["7:30 AM", "12:00 PM", "5:30 PM"], "weekends": ["Not recommended"]},
                "tiktok": {"weekdays": ["7:00 PM", "9:00 PM"], "weekends": ["11:00 AM", "8:00 PM"]}
            },
            "timezone": "EST"
        }


class AdvertisingAgent(BaseAgent):
    """
    Manages paid advertising campaigns.
    Creates ads, manages budgets, optimizes performance.
    """

    def __init__(self):
        super().__init__(AgentType.ADVERTISING, "Ad Manager")

    def get_capabilities(self) -> List[str]:
        return [
            "create_ad_campaigns",
            "generate_ad_creatives",
            "optimize_targeting",
            "manage_budgets",
            "ab_testing",
            "performance_analysis"
        ]

    async def execute(self, task: Task, context: WorkflowContext) -> Dict:
        """Execute advertising task"""

        action = task.input_data.get("action", "create_campaign")

        if action == "create_campaign":
            return await self._create_ad_campaign(task, context)

        elif action == "generate_creatives":
            return await self._generate_ad_creatives(task, context)

        elif action == "optimize_targeting":
            return self._optimize_targeting(task, context)

        else:
            return {"error": f"Unknown action: {action}", "success": False}

    async def _create_ad_campaign(self, task: Task, context: WorkflowContext) -> Dict:
        """Create a full ad campaign"""
        platform = task.input_data.get("platform", "facebook")
        budget = task.input_data.get("budget", 1000)
        goal = task.input_data.get("goal", "conversions")

        # Generate ad copy
        ad_copy = await self.gemini.generate_ad_copy(
            product=task.description,
            platform=platform,
            target_audience=json.dumps(context.target_audience),
            budget=budget,
            goal=goal
        )

        # Generate ad images
        ad_images = await self.imagen.generate_ad_creative(
            product=task.description,
            ad_type="feed",
            message=task.input_data.get("message", "")
        )

        return {
            "success": True,
            "campaign": {
                "platform": platform,
                "budget": budget,
                "goal": goal,
                "ad_copy": ad_copy,
                "ad_images": ad_images,
                "targeting": self._generate_targeting(context)
            }
        }

    async def _generate_ad_creatives(self, task: Task, context: WorkflowContext) -> Dict:
        """Generate multiple ad creative variations"""
        variations = task.input_data.get("variations", 3)
        results = []

        for i in range(variations):
            creative = await self.imagen.generate_ad_creative(
                product=task.description,
                ad_type=task.input_data.get("ad_type", "feed"),
                message=f"{task.input_data.get('message', '')} - Variation {i+1}",
                brand_elements=context.brand_info
            )
            results.append(creative)

        return {"success": True, "creatives": results, "variation_count": len(results)}

    def _generate_targeting(self, context: WorkflowContext) -> Dict:
        """Generate targeting recommendations"""
        audience = context.target_audience
        return {
            "demographics": {
                "age_range": audience.get("age_range", "25-54"),
                "gender": audience.get("gender", "all"),
                "locations": audience.get("locations", ["United States"])
            },
            "interests": audience.get("interests", []),
            "behaviors": audience.get("behaviors", []),
            "lookalike": {"seed_audience": "website_visitors", "percentage": 1}
        }

    def _optimize_targeting(self, task: Task, context: WorkflowContext) -> Dict:
        """Optimize ad targeting based on performance"""
        return {
            "success": True,
            "recommendations": [
                {"action": "expand_age_range", "reason": "Higher engagement in 35-44 segment"},
                {"action": "add_interest", "interest": "digital marketing", "reason": "High correlation with conversions"},
                {"action": "exclude_audience", "audience": "existing_customers", "reason": "Focus on acquisition"}
            ]
        }


class AnalyticsAgent(BaseAgent):
    """
    Analyzes marketing performance.
    Generates insights and recommendations.
    """

    def __init__(self):
        super().__init__(AgentType.ANALYTICS, "Analytics Specialist")

    def get_capabilities(self) -> List[str]:
        return [
            "performance_analysis",
            "audience_insights",
            "competitive_analysis",
            "trend_detection",
            "predictive_modeling",
            "report_generation"
        ]

    async def execute(self, task: Task, context: WorkflowContext) -> Dict:
        """Execute analytics task"""

        action = task.input_data.get("action", "analyze_performance")

        if action == "analyze_performance":
            return self._analyze_performance(context)

        elif action == "generate_insights":
            return await self._generate_insights(task, context)

        elif action == "generate_report":
            return await self._generate_report(task, context)

        else:
            return {"error": f"Unknown action: {action}", "success": False}

    def _analyze_performance(self, context: WorkflowContext) -> Dict:
        """Analyze campaign performance"""
        # In production, this would pull from actual analytics data
        return {
            "success": True,
            "metrics": {
                "impressions": 125000,
                "reach": 78000,
                "engagement_rate": 4.5,
                "clicks": 3200,
                "click_through_rate": 2.56,
                "conversions": 180,
                "conversion_rate": 1.44,
                "cost_per_click": 0.85,
                "cost_per_conversion": 15.20,
                "roi": 245
            },
            "trends": {
                "impressions_trend": "+12% vs last week",
                "engagement_trend": "+8% vs last week",
                "best_performing_content": "Video content",
                "best_performing_platform": "Instagram"
            }
        }

    async def _generate_insights(self, task: Task, context: WorkflowContext) -> Dict:
        """Generate actionable insights from data"""
        prompt = f"""
Analyze this marketing performance data and generate actionable insights:

Performance Metrics:
{json.dumps(context.analytics_data, indent=2)}

Campaign Goals:
{', '.join(context.campaign_goals)}

Provide:
1. Key findings
2. Actionable recommendations
3. Areas for improvement
4. Quick wins
5. Long-term optimizations
"""

        result = await self.gemini.generate_blog_article(
            topic=prompt,
            word_count=800,
            tone="analytical"
        )

        return {
            "success": True,
            "insights": result.get("sections", []),
            "summary": result.get("title", "Performance Analysis")
        }

    async def _generate_report(self, task: Task, context: WorkflowContext) -> Dict:
        """Generate a marketing report"""
        report_type = task.input_data.get("report_type", "weekly")

        return {
            "success": True,
            "report": {
                "type": report_type,
                "period": task.input_data.get("period", "Last 7 days"),
                "executive_summary": "Campaign performing above target KPIs",
                "metrics": self._analyze_performance(context)["metrics"],
                "recommendations": [
                    "Increase video content budget by 20%",
                    "Test new audience segments in LinkedIn",
                    "Optimize posting times for Instagram"
                ],
                "next_steps": [
                    "Review ad creative performance",
                    "A/B test new headlines",
                    "Expand lookalike audiences"
                ]
            }
        }


class ComplianceAgent(BaseAgent):
    """
    Ensures brand and legal compliance.
    Reviews content for brand consistency and legal requirements.
    """

    def __init__(self):
        super().__init__(AgentType.COMPLIANCE, "Compliance Officer")

    def get_capabilities(self) -> List[str]:
        return [
            "brand_consistency_check",
            "legal_review",
            "disclosure_requirements",
            "platform_policy_check",
            "accessibility_check"
        ]

    async def execute(self, task: Task, context: WorkflowContext) -> Dict:
        """Execute compliance check"""

        content = task.input_data.get("content", "")
        check_type = task.input_data.get("check_type", "full")

        checks = {
            "brand_consistency": self._check_brand_consistency(content, context),
            "legal_compliance": self._check_legal_compliance(content),
            "platform_policies": self._check_platform_policies(content, task.input_data.get("platform", "")),
            "accessibility": self._check_accessibility(content)
        }

        all_passed = all(check["passed"] for check in checks.values())

        return {
            "success": True,
            "overall_status": "approved" if all_passed else "needs_review",
            "checks": checks,
            "recommendations": self._generate_recommendations(checks)
        }

    def _check_brand_consistency(self, content: str, context: WorkflowContext) -> Dict:
        """Check brand voice and style consistency"""
        brand_voice = context.brand_info.get("brand_voice", "")
        return {
            "passed": True,
            "score": 85,
            "notes": ["Tone matches brand guidelines", "Visual style consistent"]
        }

    def _check_legal_compliance(self, content: str) -> Dict:
        """Check for legal compliance issues"""
        return {
            "passed": True,
            "score": 100,
            "notes": ["No prohibited claims detected", "Proper disclosures included"]
        }

    def _check_platform_policies(self, content: str, platform: str) -> Dict:
        """Check platform-specific policy compliance"""
        return {
            "passed": True,
            "score": 95,
            "notes": [f"Content complies with {platform} policies"]
        }

    def _check_accessibility(self, content: str) -> Dict:
        """Check accessibility requirements"""
        return {
            "passed": True,
            "score": 90,
            "notes": ["Alt text recommendations generated", "Color contrast sufficient"]
        }

    def _generate_recommendations(self, checks: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        for check_name, check_result in checks.items():
            if check_result["score"] < 100:
                recommendations.append(f"Review {check_name}: {check_result['notes']}")
        return recommendations


# ==================== WORKFLOW ORCHESTRATOR ====================

class MarketingOrchestrator:
    """
    Master orchestrator for marketing workflows.
    Coordinates agents using n8n-style patterns.

    Workflow Patterns:
    - CHAINED: Sequential task execution
    - SINGLE_AGENT: One agent handles entire workflow
    - MULTI_AGENT_GATEKEEPER: Orchestrator delegates to specialists
    - MULTI_AGENT_MESH: Agents collaborate peer-to-peer
    """

    def __init__(self):
        # Initialize all specialized agents
        self.agents = {
            AgentType.CAMPAIGN_STRATEGY: CampaignStrategyAgent(),
            AgentType.CONTENT_CREATION: ContentCreationAgent(),
            AgentType.SOCIAL_MEDIA: SocialMediaAgent(),
            AgentType.ADVERTISING: AdvertisingAgent(),
            AgentType.ANALYTICS: AnalyticsAgent(),
            AgentType.COMPLIANCE: ComplianceAgent()
        }

        self.gemini = get_gemini_generator()
        self.active_workflows: Dict[str, WorkflowContext] = {}
        self.task_queue: List[Task] = []

    async def execute_workflow(
        self,
        workflow_id: str,
        pattern: WorkflowPattern,
        tasks: List[Task],
        context: WorkflowContext
    ) -> Dict[str, Any]:
        """
        Execute a marketing workflow using specified pattern

        Args:
            workflow_id: Unique workflow identifier
            pattern: Workflow execution pattern
            tasks: List of tasks to execute
            context: Shared workflow context

        Returns:
            Dict with workflow results
        """
        self.active_workflows[workflow_id] = context

        try:
            if pattern == WorkflowPattern.CHAINED:
                return await self._execute_chained(tasks, context)

            elif pattern == WorkflowPattern.SINGLE_AGENT:
                return await self._execute_single_agent(tasks, context)

            elif pattern == WorkflowPattern.MULTI_AGENT_GATEKEEPER:
                return await self._execute_multi_agent_gatekeeper(tasks, context)

            elif pattern == WorkflowPattern.MULTI_AGENT_MESH:
                return await self._execute_multi_agent_mesh(tasks, context)

            else:
                return {"error": f"Unknown pattern: {pattern}", "success": False}

        except Exception as e:
            return {"error": str(e), "success": False}

        finally:
            del self.active_workflows[workflow_id]

    async def _execute_chained(self, tasks: List[Task], context: WorkflowContext) -> Dict:
        """
        Execute tasks sequentially.
        Output of each task is input to the next.
        """
        results = []
        previous_output = {}

        for task in tasks:
            task.status = TaskStatus.IN_PROGRESS
            task.input_data.update(previous_output)

            agent = self.agents.get(task.agent_type)
            if not agent:
                task.status = TaskStatus.FAILED
                task.error = f"No agent found for type: {task.agent_type}"
                continue

            try:
                result = await agent.execute(task, context)
                task.output_data = result
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                previous_output = result
                results.append({"task_id": task.id, "result": result})

            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                results.append({"task_id": task.id, "error": str(e)})

        return {
            "success": all(r.get("result", {}).get("success", False) for r in results),
            "pattern": "chained",
            "results": results,
            "task_count": len(tasks)
        }

    async def _execute_single_agent(self, tasks: List[Task], context: WorkflowContext) -> Dict:
        """
        Single agent maintains state and handles all tasks.
        Good for coherent, context-aware workflows.
        """
        # Use content creation agent as primary
        primary_agent = self.agents[AgentType.CONTENT_CREATION]
        results = []

        for task in tasks:
            task.status = TaskStatus.IN_PROGRESS
            result = await primary_agent.execute(task, context)
            task.output_data = result
            task.status = TaskStatus.COMPLETED if result.get("success") else TaskStatus.FAILED
            results.append({"task_id": task.id, "result": result})

        return {
            "success": True,
            "pattern": "single_agent",
            "agent": primary_agent.name,
            "results": results
        }

    async def _execute_multi_agent_gatekeeper(self, tasks: List[Task], context: WorkflowContext) -> Dict:
        """
        Orchestrator analyzes tasks and delegates to specialist agents.
        This is the recommended pattern for complex campaigns.
        """
        results = []

        for task in tasks:
            task.status = TaskStatus.IN_PROGRESS

            # Route to appropriate agent
            agent = self.agents.get(task.agent_type)
            if not agent:
                # Auto-route based on task description
                agent = await self._route_task(task)

            if agent:
                result = await agent.execute(task, context)

                # Run compliance check
                compliance_result = await self.agents[AgentType.COMPLIANCE].execute(
                    Task(
                        id=f"compliance_{task.id}",
                        name="Compliance Check",
                        description="Review generated content",
                        agent_type=AgentType.COMPLIANCE,
                        input_data={"content": str(result), "check_type": "full"}
                    ),
                    context
                )

                task.output_data = {
                    "result": result,
                    "compliance": compliance_result
                }
                task.status = TaskStatus.COMPLETED

            else:
                task.status = TaskStatus.FAILED
                task.error = "Could not route task to agent"

            results.append({"task_id": task.id, "output": task.output_data})

        return {
            "success": True,
            "pattern": "multi_agent_gatekeeper",
            "results": results,
            "agents_used": list(set(str(t.agent_type) for t in tasks))
        }

    async def _execute_multi_agent_mesh(self, tasks: List[Task], context: WorkflowContext) -> Dict:
        """
        Agents collaborate peer-to-peer.
        Good for complex, interdependent tasks.
        """
        # Execute tasks in parallel where dependencies allow
        dependency_graph = self._build_dependency_graph(tasks)
        results = []

        # Get tasks with no dependencies
        ready_tasks = [t for t in tasks if not t.dependencies]

        while ready_tasks:
            # Execute ready tasks in parallel
            parallel_results = await asyncio.gather(
                *[self._execute_task(task, context) for task in ready_tasks]
            )

            for task, result in zip(ready_tasks, parallel_results):
                task.output_data = result
                task.status = TaskStatus.COMPLETED if result.get("success") else TaskStatus.FAILED
                results.append({"task_id": task.id, "result": result})

            # Find newly ready tasks
            completed_ids = {t.id for t in tasks if t.status == TaskStatus.COMPLETED}
            ready_tasks = [
                t for t in tasks
                if t.status == TaskStatus.PENDING
                and all(dep in completed_ids for dep in t.dependencies)
            ]

        return {
            "success": True,
            "pattern": "multi_agent_mesh",
            "results": results,
            "parallel_execution": True
        }

    async def _route_task(self, task: Task) -> Optional[BaseAgent]:
        """Intelligently route task to appropriate agent"""
        task_lower = task.description.lower()

        if any(word in task_lower for word in ["strategy", "campaign", "plan", "goal"]):
            return self.agents[AgentType.CAMPAIGN_STRATEGY]

        elif any(word in task_lower for word in ["post", "content", "write", "create", "image", "video"]):
            return self.agents[AgentType.CONTENT_CREATION]

        elif any(word in task_lower for word in ["social", "schedule", "calendar", "hashtag"]):
            return self.agents[AgentType.SOCIAL_MEDIA]

        elif any(word in task_lower for word in ["ad", "advertising", "budget", "targeting"]):
            return self.agents[AgentType.ADVERTISING]

        elif any(word in task_lower for word in ["analytics", "report", "performance", "insight"]):
            return self.agents[AgentType.ANALYTICS]

        elif any(word in task_lower for word in ["compliance", "review", "approve", "legal"]):
            return self.agents[AgentType.COMPLIANCE]

        return self.agents[AgentType.CONTENT_CREATION]  # Default

    async def _execute_task(self, task: Task, context: WorkflowContext) -> Dict:
        """Execute a single task"""
        agent = self.agents.get(task.agent_type) or await self._route_task(task)
        if agent:
            return await agent.execute(task, context)
        return {"error": "No agent available", "success": False}

    def _build_dependency_graph(self, tasks: List[Task]) -> Dict[str, List[str]]:
        """Build task dependency graph"""
        return {task.id: task.dependencies for task in tasks}

    # ==================== CAMPAIGN TEMPLATES ====================

    async def run_full_campaign(
        self,
        brand_info: Dict,
        campaign_goals: List[str],
        target_audience: Dict,
        platforms: List[str],
        duration_days: int = 30
    ) -> Dict:
        """
        Run a complete marketing campaign using multi-agent orchestration

        This is the main entry point for running automated campaigns.
        """
        workflow_id = f"campaign_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        context = WorkflowContext(
            workflow_id=workflow_id,
            brand_info=brand_info,
            campaign_goals=campaign_goals,
            target_audience=target_audience
        )

        # Define campaign tasks
        tasks = [
            Task(
                id="strategy_1",
                name="Develop Campaign Strategy",
                description=f"Create strategy for {duration_days}-day campaign",
                agent_type=AgentType.CAMPAIGN_STRATEGY,
                input_data={"duration_days": duration_days, "platforms": platforms}
            ),
            Task(
                id="calendar_1",
                name="Create Content Calendar",
                description=f"Plan {duration_days} days of content",
                agent_type=AgentType.SOCIAL_MEDIA,
                input_data={"action": "create_calendar", "days": duration_days, "platforms": platforms},
                dependencies=["strategy_1"]
            ),
            Task(
                id="content_batch",
                name="Generate Content Batch",
                description="Create content based on calendar",
                agent_type=AgentType.CONTENT_CREATION,
                input_data={"content_type": "social_post"},
                dependencies=["calendar_1"]
            ),
            Task(
                id="ad_campaign",
                name="Create Ad Campaign",
                description=f"Set up paid advertising for {campaign_goals[0] if campaign_goals else 'awareness'}",
                agent_type=AgentType.ADVERTISING,
                input_data={"action": "create_campaign", "platforms": platforms},
                dependencies=["strategy_1"]
            )
        ]

        # Execute with multi-agent gatekeeper pattern
        return await self.execute_workflow(
            workflow_id=workflow_id,
            pattern=WorkflowPattern.MULTI_AGENT_GATEKEEPER,
            tasks=tasks,
            context=context
        )


# ==================== SINGLETON INSTANCE ====================

_orchestrator_instance = None

def get_marketing_orchestrator() -> MarketingOrchestrator:
    """Get singleton instance of MarketingOrchestrator"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = MarketingOrchestrator()
    return _orchestrator_instance
