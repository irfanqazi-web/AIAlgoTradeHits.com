"""
MarketingAI - AI API Routes
Flask Blueprint for AI generation endpoints
"""
import os
import json
import asyncio
from datetime import datetime
from flask import Blueprint, request, jsonify
from functools import wraps

# Import AI modules
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

# Create Blueprint
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# Helper to run async functions
def run_async(coro):
    """Helper to run async coroutines in Flask"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def async_route(f):
    """Decorator to handle async routes in Flask"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return run_async(f(*args, **kwargs))
    return wrapper


# ==================== TEXT GENERATION (Gemini) ====================

@ai_bp.route('/text/social-post', methods=['POST'])
@async_route
async def generate_social_post():
    """
    Generate social media post

    Request body:
    {
        "prompt": "Post topic or description",
        "platform": "instagram|facebook|linkedin|twitter|tiktok",
        "tone": "professional|casual|humorous|inspiring",
        "brand_voice": "Brand personality description",
        "target_audience": "Target demographic",
        "include_hashtags": true,
        "include_emojis": true
    }
    """
    try:
        data = request.get_json()
        gemini = get_gemini_generator()

        result = await gemini.generate_social_post(
            prompt=data.get('prompt', ''),
            platform=data.get('platform', 'instagram'),
            tone=data.get('tone', 'professional'),
            brand_voice=data.get('brand_voice', ''),
            target_audience=data.get('target_audience', ''),
            include_hashtags=data.get('include_hashtags', True),
            include_emojis=data.get('include_emojis', True)
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@ai_bp.route('/text/content-calendar', methods=['POST'])
@async_route
async def generate_content_calendar():
    """
    Generate content calendar

    Request body:
    {
        "days": 7,
        "platforms": ["instagram", "twitter", "linkedin"],
        "brand_voice": "Brand personality",
        "content_pillars": ["education", "promotion", "entertainment"],
        "posting_frequency": "daily"
    }
    """
    try:
        data = request.get_json()
        gemini = get_gemini_generator()

        result = await gemini.generate_content_calendar(
            days=data.get('days', 7),
            platforms=data.get('platforms', ['instagram']),
            brand_voice=data.get('brand_voice', ''),
            content_pillars=data.get('content_pillars', []),
            posting_frequency=data.get('posting_frequency', 'daily')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@ai_bp.route('/text/blog', methods=['POST'])
@async_route
async def generate_blog():
    """
    Generate blog article

    Request body:
    {
        "topic": "Article topic",
        "keywords": ["keyword1", "keyword2"],
        "word_count": 1500,
        "tone": "informative",
        "seo_optimize": true
    }
    """
    try:
        data = request.get_json()
        gemini = get_gemini_generator()

        result = await gemini.generate_blog_article(
            topic=data.get('topic', ''),
            keywords=data.get('keywords', []),
            word_count=data.get('word_count', 1500),
            tone=data.get('tone', 'informative'),
            seo_optimize=data.get('seo_optimize', True)
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@ai_bp.route('/text/email', methods=['POST'])
@async_route
async def generate_email():
    """
    Generate email campaign

    Request body:
    {
        "campaign_goal": "Campaign objective",
        "audience_segment": "Target audience",
        "brand_voice": "Brand personality",
        "cta": "Call to action",
        "email_type": "promotional|newsletter|welcome|abandoned_cart"
    }
    """
    try:
        data = request.get_json()
        gemini = get_gemini_generator()

        result = await gemini.generate_email_campaign(
            campaign_goal=data.get('campaign_goal', ''),
            audience_segment=data.get('audience_segment', ''),
            brand_voice=data.get('brand_voice', ''),
            cta=data.get('cta', ''),
            email_type=data.get('email_type', 'promotional')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@ai_bp.route('/text/ad-copy', methods=['POST'])
@async_route
async def generate_ad_copy():
    """
    Generate ad copy

    Request body:
    {
        "product": "Product description",
        "platform": "google|facebook|instagram|linkedin|tiktok",
        "ad_format": "feed|story|search|display",
        "target_audience": "Target demographic",
        "budget": 100,
        "goal": "conversions|traffic|awareness"
    }
    """
    try:
        data = request.get_json()
        gemini = get_gemini_generator()

        result = await gemini.generate_ad_copy(
            product=data.get('product', ''),
            platform=data.get('platform', 'facebook'),
            ad_format=data.get('ad_format', 'feed'),
            target_audience=data.get('target_audience', ''),
            budget=data.get('budget', 100),
            goal=data.get('goal', 'conversions')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@ai_bp.route('/text/video-script', methods=['POST'])
@async_route
async def generate_video_script():
    """
    Generate video script

    Request body:
    {
        "topic": "Video topic",
        "platform": "tiktok|instagram_reel|youtube_short",
        "duration": 60,
        "style": "educational|entertaining|promotional"
    }
    """
    try:
        data = request.get_json()
        gemini = get_gemini_generator()

        result = await gemini.generate_video_script(
            topic=data.get('topic', ''),
            platform=data.get('platform', 'tiktok'),
            duration=data.get('duration', 60),
            style=data.get('style', 'educational')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ==================== IMAGE GENERATION (Imagen 4) ====================

@ai_bp.route('/image/social-graphic', methods=['POST'])
@async_route
async def generate_social_graphic():
    """
    Generate social media graphic

    Request body:
    {
        "prompt": "Image description",
        "platform": "instagram|facebook|linkedin|twitter",
        "style": "professional|playful|minimalist|bold",
        "brand_colors": ["#FF5733", "#33FF57"],
        "include_text_space": true,
        "num_images": 4
    }
    """
    try:
        data = request.get_json()
        imagen = get_imagen_generator()

        result = await imagen.generate_social_graphic(
            prompt=data.get('prompt', ''),
            platform=data.get('platform', 'instagram'),
            style=data.get('style', 'professional'),
            brand_colors=data.get('brand_colors'),
            include_text_space=data.get('include_text_space', True),
            num_images=data.get('num_images', 4)
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@ai_bp.route('/image/product', methods=['POST'])
@async_route
async def generate_product_image():
    """
    Generate product image

    Request body:
    {
        "product_description": "Product details",
        "background": "studio|lifestyle|flat_lay",
        "angle": "hero|overhead|side",
        "lighting": "soft|dramatic|natural",
        "props": ["prop1", "prop2"]
    }
    """
    try:
        data = request.get_json()
        imagen = get_imagen_generator()

        result = await imagen.generate_product_image(
            product_description=data.get('product_description', ''),
            background=data.get('background', 'studio'),
            angle=data.get('angle', 'hero'),
            lighting=data.get('lighting', 'soft'),
            props=data.get('props')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@ai_bp.route('/image/ad-creative', methods=['POST'])
@async_route
async def generate_ad_creative():
    """
    Generate ad creative images

    Request body:
    {
        "product": "Product description",
        "ad_type": "display|social|banner",
        "message": "Key message",
        "cta": "Call to action",
        "sizes": ["1:1", "16:9", "9:16"]
    }
    """
    try:
        data = request.get_json()
        imagen = get_imagen_generator()

        result = await imagen.generate_ad_creative(
            product=data.get('product', ''),
            ad_type=data.get('ad_type', 'display'),
            message=data.get('message', ''),
            cta=data.get('cta', ''),
            sizes=data.get('sizes')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@ai_bp.route('/image/brand-visuals', methods=['POST'])
@async_route
async def generate_brand_visuals():
    """
    Generate brand visual assets

    Request body:
    {
        "brand_name": "Company name",
        "industry": "Business industry",
        "style": "modern|classic|playful|luxurious",
        "colors": ["#FF5733", "#33FF57"],
        "visual_types": ["hero_banner", "pattern", "icon_style"]
    }
    """
    try:
        data = request.get_json()
        imagen = get_imagen_generator()

        result = await imagen.generate_brand_visuals(
            brand_name=data.get('brand_name', ''),
            industry=data.get('industry', ''),
            style=data.get('style', 'modern'),
            colors=data.get('colors'),
            visual_types=data.get('visual_types')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ==================== VIDEO GENERATION (Veo) ====================

@ai_bp.route('/video/social', methods=['POST'])
@async_route
async def generate_social_video():
    """
    Generate social media video

    Request body:
    {
        "prompt": "Video description",
        "platform": "tiktok|instagram_reel|youtube_short",
        "duration": 15,
        "style": "cinematic|documentary|dynamic",
        "include_motion": "subtle|moderate|dynamic"
    }
    """
    try:
        data = request.get_json()
        veo = get_veo_generator()

        result = await veo.generate_social_video(
            prompt=data.get('prompt', ''),
            platform=data.get('platform', 'tiktok'),
            duration=data.get('duration', 15),
            style=data.get('style', 'cinematic'),
            include_motion=data.get('include_motion', 'moderate')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@ai_bp.route('/video/product', methods=['POST'])
@async_route
async def generate_product_video():
    """
    Generate product showcase video

    Request body:
    {
        "product_description": "Product details",
        "video_type": "showcase|demo|lifestyle",
        "duration": 15,
        "background": "studio|lifestyle",
        "camera_movement": "orbit|zoom|static"
    }
    """
    try:
        data = request.get_json()
        veo = get_veo_generator()

        result = await veo.generate_product_video(
            product_description=data.get('product_description', ''),
            video_type=data.get('video_type', 'showcase'),
            duration=data.get('duration', 15),
            background=data.get('background', 'studio'),
            camera_movement=data.get('camera_movement', 'orbit')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@ai_bp.route('/video/ad', methods=['POST'])
@async_route
async def generate_ad_video():
    """
    Generate advertising video

    Request body:
    {
        "product": "Product description",
        "ad_platform": "facebook|instagram|youtube|tiktok",
        "target_audience": "Target demographic",
        "key_message": "Main message",
        "duration": 15,
        "cta": "Call to action"
    }
    """
    try:
        data = request.get_json()
        veo = get_veo_generator()

        result = await veo.generate_ad_video(
            product=data.get('product', ''),
            ad_platform=data.get('ad_platform', 'facebook'),
            target_audience=data.get('target_audience', ''),
            key_message=data.get('key_message', ''),
            duration=data.get('duration', 15),
            cta=data.get('cta', 'Learn More')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ==================== AUDIO GENERATION (Lyria 2) ====================

@ai_bp.route('/audio/background-music', methods=['POST'])
@async_route
async def generate_background_music():
    """
    Generate background music

    Request body:
    {
        "mood": "uplifting|calm|energetic|dramatic",
        "genre": "corporate|electronic|acoustic|cinematic",
        "duration": 30,
        "tempo": "slow|moderate|fast",
        "use_case": "video_background|podcast_intro|ad_music"
    }
    """
    try:
        data = request.get_json()
        lyria = get_lyria_generator()

        result = await lyria.generate_background_music(
            mood=data.get('mood', 'uplifting'),
            genre=data.get('genre', 'corporate'),
            duration=data.get('duration', 30),
            tempo=data.get('tempo', 'moderate'),
            use_case=data.get('use_case', 'video_background')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@ai_bp.route('/audio/jingle', methods=['POST'])
@async_route
async def generate_jingle():
    """
    Generate brand jingle

    Request body:
    {
        "brand_name": "Company name",
        "tagline": "Brand tagline",
        "style": "modern|classic|playful|premium",
        "duration": 15,
        "include_vocals": false
    }
    """
    try:
        data = request.get_json()
        lyria = get_lyria_generator()

        result = await lyria.generate_jingle(
            brand_name=data.get('brand_name', ''),
            tagline=data.get('tagline', ''),
            style=data.get('style', 'modern'),
            duration=data.get('duration', 15),
            include_vocals=data.get('include_vocals', False)
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@ai_bp.route('/audio/podcast', methods=['POST'])
@async_route
async def generate_podcast_audio():
    """
    Generate podcast audio elements

    Request body:
    {
        "podcast_name": "Podcast name",
        "element_type": "intro|outro|transition|bed_music",
        "style": "professional|casual|energetic",
        "duration": 15
    }
    """
    try:
        data = request.get_json()
        lyria = get_lyria_generator()

        result = await lyria.generate_podcast_elements(
            podcast_name=data.get('podcast_name', ''),
            element_type=data.get('element_type', 'intro'),
            style=data.get('style', 'professional'),
            duration=data.get('duration', 15)
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ==================== AGENTIC WORKFLOWS ====================

@ai_bp.route('/agents/run-campaign', methods=['POST'])
@async_route
async def run_campaign():
    """
    Run full marketing campaign using multi-agent orchestration

    Request body:
    {
        "brand_info": {
            "name": "Brand name",
            "brand_voice": "Brand personality",
            "colors": ["#FF5733"]
        },
        "campaign_goals": ["awareness", "engagement"],
        "target_audience": {
            "age_range": "25-45",
            "interests": ["technology", "business"]
        },
        "platforms": ["instagram", "linkedin", "twitter"],
        "duration_days": 30
    }
    """
    try:
        data = request.get_json()
        orchestrator = get_marketing_orchestrator()

        result = await orchestrator.run_full_campaign(
            brand_info=data.get('brand_info', {}),
            campaign_goals=data.get('campaign_goals', []),
            target_audience=data.get('target_audience', {}),
            platforms=data.get('platforms', ['instagram']),
            duration_days=data.get('duration_days', 30)
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@ai_bp.route('/agents/execute-task', methods=['POST'])
@async_route
async def execute_agent_task():
    """
    Execute a single agent task

    Request body:
    {
        "task_name": "Task name",
        "task_description": "What to do",
        "agent_type": "content_creation|social_media|advertising|analytics",
        "input_data": {},
        "brand_info": {},
        "target_audience": {}
    }
    """
    try:
        data = request.get_json()
        orchestrator = get_marketing_orchestrator()

        # Map agent type string to enum
        agent_type_map = {
            "campaign_strategy": AgentType.CAMPAIGN_STRATEGY,
            "content_creation": AgentType.CONTENT_CREATION,
            "social_media": AgentType.SOCIAL_MEDIA,
            "advertising": AgentType.ADVERTISING,
            "analytics": AgentType.ANALYTICS,
            "compliance": AgentType.COMPLIANCE
        }

        agent_type = agent_type_map.get(
            data.get('agent_type', 'content_creation'),
            AgentType.CONTENT_CREATION
        )

        # Create task
        task = Task(
            id=f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            name=data.get('task_name', 'Agent Task'),
            description=data.get('task_description', ''),
            agent_type=agent_type,
            input_data=data.get('input_data', {})
        )

        # Create context
        context = WorkflowContext(
            workflow_id=f"single_{task.id}",
            brand_info=data.get('brand_info', {}),
            campaign_goals=data.get('campaign_goals', []),
            target_audience=data.get('target_audience', {})
        )

        # Execute
        agent = orchestrator.agents.get(agent_type)
        if agent:
            result = await agent.execute(task, context)
            return jsonify(result)
        else:
            return jsonify({"error": f"Agent not found: {agent_type}", "success": False}), 400

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@ai_bp.route('/agents/workflow', methods=['POST'])
@async_route
async def execute_workflow():
    """
    Execute custom workflow with multiple tasks

    Request body:
    {
        "workflow_pattern": "chained|single_agent|multi_agent_gatekeeper|multi_agent_mesh",
        "tasks": [
            {
                "id": "task_1",
                "name": "Task name",
                "description": "Task description",
                "agent_type": "content_creation",
                "input_data": {},
                "dependencies": []
            }
        ],
        "context": {
            "brand_info": {},
            "campaign_goals": [],
            "target_audience": {}
        }
    }
    """
    try:
        data = request.get_json()
        orchestrator = get_marketing_orchestrator()

        # Map pattern string to enum
        pattern_map = {
            "chained": WorkflowPattern.CHAINED,
            "single_agent": WorkflowPattern.SINGLE_AGENT,
            "multi_agent_gatekeeper": WorkflowPattern.MULTI_AGENT_GATEKEEPER,
            "multi_agent_mesh": WorkflowPattern.MULTI_AGENT_MESH
        }

        pattern = pattern_map.get(
            data.get('workflow_pattern', 'multi_agent_gatekeeper'),
            WorkflowPattern.MULTI_AGENT_GATEKEEPER
        )

        # Map agent types
        agent_type_map = {
            "campaign_strategy": AgentType.CAMPAIGN_STRATEGY,
            "content_creation": AgentType.CONTENT_CREATION,
            "social_media": AgentType.SOCIAL_MEDIA,
            "advertising": AgentType.ADVERTISING,
            "analytics": AgentType.ANALYTICS,
            "compliance": AgentType.COMPLIANCE
        }

        # Create tasks
        tasks = []
        for task_data in data.get('tasks', []):
            task = Task(
                id=task_data.get('id', f"task_{len(tasks)}"),
                name=task_data.get('name', ''),
                description=task_data.get('description', ''),
                agent_type=agent_type_map.get(
                    task_data.get('agent_type', 'content_creation'),
                    AgentType.CONTENT_CREATION
                ),
                input_data=task_data.get('input_data', {}),
                dependencies=task_data.get('dependencies', [])
            )
            tasks.append(task)

        # Create context
        ctx_data = data.get('context', {})
        context = WorkflowContext(
            workflow_id=f"workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            brand_info=ctx_data.get('brand_info', {}),
            campaign_goals=ctx_data.get('campaign_goals', []),
            target_audience=ctx_data.get('target_audience', {})
        )

        # Execute workflow
        result = await orchestrator.execute_workflow(
            workflow_id=context.workflow_id,
            pattern=pattern,
            tasks=tasks,
            context=context
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ==================== HEALTH & STATUS ====================

@ai_bp.route('/health', methods=['GET'])
def ai_health():
    """Check AI services health"""
    return jsonify({
        "status": "healthy",
        "services": {
            "gemini": "available",
            "imagen": "available",
            "veo": "pending_access",
            "lyria": "pending_access"
        },
        "agents": [
            "campaign_strategy",
            "content_creation",
            "social_media",
            "advertising",
            "analytics",
            "compliance"
        ],
        "timestamp": datetime.utcnow().isoformat()
    })


@ai_bp.route('/capabilities', methods=['GET'])
def get_capabilities():
    """Get all AI capabilities"""
    return jsonify({
        "text_generation": {
            "model": "Gemini 2.5 Pro/Flash",
            "capabilities": [
                "social_posts",
                "content_calendars",
                "blog_articles",
                "email_campaigns",
                "ad_copy",
                "video_scripts"
            ]
        },
        "image_generation": {
            "model": "Imagen 4",
            "capabilities": [
                "social_graphics",
                "product_images",
                "ad_creatives",
                "brand_visuals"
            ]
        },
        "video_generation": {
            "model": "Veo 2/3",
            "capabilities": [
                "social_videos",
                "product_videos",
                "ad_videos",
                "video_with_audio"
            ],
            "note": "Veo 3 requires private preview access"
        },
        "audio_generation": {
            "model": "Lyria 2",
            "capabilities": [
                "background_music",
                "jingles",
                "podcast_elements",
                "ad_music"
            ]
        },
        "agentic_workflows": {
            "framework": "Custom (n8n-inspired)",
            "patterns": [
                "chained",
                "single_agent",
                "multi_agent_gatekeeper",
                "multi_agent_mesh"
            ],
            "agents": [
                "CampaignStrategyAgent",
                "ContentCreationAgent",
                "SocialMediaAgent",
                "AdvertisingAgent",
                "AnalyticsAgent",
                "ComplianceAgent"
            ]
        }
    })
