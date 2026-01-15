"""
Platform Specifications for MarketingAI
Complete specs for TikTok, Instagram, YouTube, Facebook, LinkedIn
With Canva + Gemini integration for AI image/art creation
"""

# Design Tools Integration
DESIGN_TOOLS = {
    "canva": {
        "name": "Canva",
        "description": "AI-powered design platform with Gemini integration",
        "api_base": "https://api.canva.com/rest/v1",
        "features": {
            "magic_design": "AI-powered design generation from prompts",
            "magic_write": "AI copywriting powered by Gemini",
            "magic_eraser": "Remove unwanted elements",
            "magic_expand": "Extend image backgrounds",
            "magic_grab": "Move and resize objects",
            "magic_animate": "Auto-animate designs",
            "background_remover": "Instant background removal",
            "text_to_image": "Generate images from text prompts",
            "brand_kit": "Consistent brand assets"
        },
        "supported_formats": ["PNG", "JPG", "PDF", "MP4", "GIF", "SVG"],
        "template_categories": [
            "Social Media", "Presentations", "Videos", "Print",
            "Marketing", "Documents", "Websites"
        ],
        "gemini_integration": {
            "model": "gemini-2.0-flash",
            "capabilities": [
                "Generate design prompts from marketing goals",
                "Create copy variations for A/B testing",
                "Suggest color palettes from brand guidelines",
                "Auto-generate hashtags and captions",
                "Analyze design effectiveness"
            ]
        }
    }
}

PLATFORM_SPECS = {
    "tiktok": {
        "name": "TikTok",
        "icon": "🎵",
        "description": "Short-form video platform for viral content",
        "content_types": {
            "video": {
                "dimensions": {"width": 1080, "height": 1920},
                "aspect_ratio": "9:16",
                "max_duration_sec": 600,
                "recommended_duration": "15-60 seconds",
                "file_formats": ["mp4", "mov"],
                "max_file_size_mb": 287
            },
            "photo": {
                "dimensions": {"width": 1080, "height": 1920},
                "aspect_ratio": "9:16",
                "max_photos": 35
            },
            "carousel": {
                "dimensions": {"width": 1080, "height": 1920},
                "max_slides": 35
            }
        },
        "caption": {
            "max_length": 2200,
            "recommended_hashtags": "3-5"
        },
        "canva_templates": ["TikTok Video", "TikTok Photo", "TikTok Carousel"],
        "best_posting_times": ["7am", "12pm", "3pm", "7pm", "10pm"],
        "ai_recommendations": [
            "Use Gemini to generate trending hook scripts",
            "Create thumbnail variations with Canva Magic Design",
            "Generate captions with Magic Write"
        ]
    },

    "instagram": {
        "name": "Instagram",
        "icon": "📸",
        "description": "Visual storytelling and community building",
        "content_types": {
            "feed_square": {"dimensions": {"width": 1080, "height": 1080}, "aspect_ratio": "1:1"},
            "feed_portrait": {"dimensions": {"width": 1080, "height": 1350}, "aspect_ratio": "4:5"},
            "carousel": {"max_slides": 10, "dimensions": {"width": 1080, "height": 1080}},
            "stories": {"dimensions": {"width": 1080, "height": 1920}, "aspect_ratio": "9:16"},
            "reels": {"dimensions": {"width": 1080, "height": 1920}, "max_duration_sec": 90}
        },
        "caption": {
            "max_length": 2200,
            "recommended_hashtags": "5-10"
        },
        "canva_templates": [
            "Instagram Post", "Instagram Story", "Instagram Reel Cover",
            "Instagram Carousel", "Instagram Highlight Cover"
        ],
        "best_posting_times": ["6am", "11am", "1pm", "7pm"],
        "ai_recommendations": [
            "Generate carousel content with Gemini",
            "Create branded templates with Canva Brand Kit",
            "Auto-resize for all Instagram formats"
        ]
    },

    "youtube": {
        "name": "YouTube",
        "icon": "▶️",
        "description": "Long-form video content and education",
        "content_types": {
            "video": {"dimensions": {"width": 1920, "height": 1080}, "aspect_ratio": "16:9"},
            "shorts": {"dimensions": {"width": 1080, "height": 1920}, "max_duration_sec": 60},
            "thumbnail": {"dimensions": {"width": 1280, "height": 720}, "aspect_ratio": "16:9"},
            "channel_banner": {"dimensions": {"width": 2560, "height": 1440}},
            "end_screen": {"dimensions": {"width": 1920, "height": 1080}}
        },
        "title": {"max_length": 100, "recommended_length": "60-70"},
        "description": {"max_length": 5000},
        "canva_templates": [
            "YouTube Thumbnail", "YouTube Channel Art", "YouTube Intro",
            "YouTube End Screen", "YouTube Shorts Cover"
        ],
        "best_posting_times": ["2pm", "4pm", "9pm"],
        "ai_recommendations": [
            "Generate click-worthy thumbnail ideas with Gemini",
            "Create A/B test thumbnail variations with Canva",
            "Auto-generate video descriptions and tags"
        ]
    },

    "facebook": {
        "name": "Facebook",
        "icon": "📘",
        "description": "Community engagement and advertising",
        "content_types": {
            "link_post": {"dimensions": {"width": 1200, "height": 630}, "aspect_ratio": "1.91:1"},
            "image_post": {"dimensions": {"width": 1200, "height": 1200}, "aspect_ratio": "1:1"},
            "video": {"dimensions": {"width": 1280, "height": 720}, "aspect_ratio": "16:9"},
            "stories": {"dimensions": {"width": 1080, "height": 1920}, "aspect_ratio": "9:16"},
            "reels": {"dimensions": {"width": 1080, "height": 1920}, "max_duration_sec": 90},
            "cover_photo": {"dimensions": {"width": 820, "height": 312}},
            "event_cover": {"dimensions": {"width": 1920, "height": 1080}}
        },
        "caption": {"max_length": 63206, "recommended_hashtags": "1-3"},
        "canva_templates": [
            "Facebook Post", "Facebook Cover", "Facebook Story",
            "Facebook Event Cover", "Facebook Ad"
        ],
        "best_posting_times": ["9am", "1pm", "3pm"],
        "ai_recommendations": [
            "Generate engaging poll questions with Gemini",
            "Create shareable graphics with Canva",
            "Optimize ad creatives with AI analysis"
        ]
    },

    "linkedin": {
        "name": "LinkedIn",
        "icon": "💼",
        "description": "Professional networking and B2B marketing",
        "content_types": {
            "text_post": {"max_length": 3000},
            "image_post": {"dimensions": {"width": 1200, "height": 627}, "aspect_ratio": "1.91:1"},
            "carousel": {"dimensions": {"width": 1080, "height": 1080}, "max_slides": 10, "format": "PDF"},
            "video": {"dimensions": {"width": 1920, "height": 1080}, "max_duration_min": 10},
            "article": {"recommended_length": "1500-2000 words"},
            "newsletter": {"subscriber_feature": True},
            "banner": {"dimensions": {"width": 1584, "height": 396}}
        },
        "caption": {"max_length": 3000, "recommended_hashtags": "3-5"},
        "canva_templates": [
            "LinkedIn Post", "LinkedIn Banner", "LinkedIn Carousel (PDF)",
            "LinkedIn Article Header", "LinkedIn Company Page"
        ],
        "best_posting_times": ["7am", "8am", "12pm", "5pm"],
        "ai_recommendations": [
            "Generate thought leadership content with Gemini",
            "Create professional PDF carousels with Canva",
            "Write compelling headlines with Magic Write"
        ]
    }
}


# Canva + Gemini AI Workflows
AI_DESIGN_WORKFLOWS = {
    "social_post_generator": {
        "name": "AI Social Post Generator",
        "description": "Generate complete social media posts with AI",
        "steps": [
            {"step": 1, "action": "input_topic", "tool": "user", "output": "topic_description"},
            {"step": 2, "action": "generate_copy", "tool": "gemini", "output": "headline, caption, hashtags"},
            {"step": 3, "action": "generate_image_prompt", "tool": "gemini", "output": "design_prompt"},
            {"step": 4, "action": "create_design", "tool": "canva_magic_design", "output": "design_url"},
            {"step": 5, "action": "resize_for_platforms", "tool": "canva_resize", "output": "platform_versions"}
        ]
    },
    "carousel_generator": {
        "name": "AI Carousel Generator",
        "description": "Create educational carousel posts",
        "steps": [
            {"step": 1, "action": "input_topic", "tool": "user", "output": "topic"},
            {"step": 2, "action": "generate_slides", "tool": "gemini", "output": "slide_content[]"},
            {"step": 3, "action": "generate_visuals", "tool": "canva_magic_design", "output": "slide_designs[]"},
            {"step": 4, "action": "apply_brand", "tool": "canva_brand_kit", "output": "branded_carousel"},
            {"step": 5, "action": "export", "tool": "canva_export", "output": "final_files"}
        ]
    },
    "video_thumbnail_generator": {
        "name": "AI Video Thumbnail Generator",
        "description": "Create click-worthy thumbnails",
        "steps": [
            {"step": 1, "action": "analyze_video", "tool": "gemini_vision", "output": "key_moments"},
            {"step": 2, "action": "generate_concepts", "tool": "gemini", "output": "thumbnail_ideas[]"},
            {"step": 3, "action": "create_variations", "tool": "canva_magic_design", "output": "thumbnails[]"},
            {"step": 4, "action": "predict_ctr", "tool": "gemini", "output": "ctr_predictions"},
            {"step": 5, "action": "select_best", "tool": "ai_ranking", "output": "recommended_thumbnail"}
        ]
    },
    "brand_content_suite": {
        "name": "Complete Brand Content Suite",
        "description": "Generate full campaign assets",
        "steps": [
            {"step": 1, "action": "input_campaign", "tool": "user", "output": "campaign_brief"},
            {"step": 2, "action": "generate_strategy", "tool": "gemini", "output": "content_strategy"},
            {"step": 3, "action": "create_content_calendar", "tool": "gemini", "output": "calendar"},
            {"step": 4, "action": "batch_create_designs", "tool": "canva_bulk", "output": "all_assets"},
            {"step": 5, "action": "schedule", "tool": "scheduler", "output": "scheduled_posts"}
        ]
    }
}


# Gemini prompts for design generation
GEMINI_DESIGN_PROMPTS = {
    "social_post": """Create a social media post for {platform} about: {topic}

Brand voice: {brand_voice}
Target audience: {audience}

Generate:
1. Attention-grabbing headline (max 60 chars)
2. Engaging caption (max {max_length} chars)
3. 5 relevant hashtags
4. Image prompt for Canva Magic Design (describe the visual in detail)
5. Call-to-action

Format as JSON.""",

    "carousel_content": """Create a {num_slides}-slide carousel for {platform} about: {topic}

Style: {style}
Audience: {audience}

For each slide, provide:
- Slide number
- Headline (max 40 chars)
- Body text (max 100 chars)
- Visual description for AI image generation
- Suggested icon or illustration

Start with a hook, end with CTA.
Format as JSON array.""",

    "thumbnail_ideas": """Generate 5 YouTube thumbnail concepts for: {video_title}

Video description: {description}
Target audience: {audience}

For each concept, provide:
- Main text overlay (max 5 words)
- Facial expression/pose if person included
- Background style
- Color scheme
- Emotion to evoke

Format as JSON array.""",

    "ad_copy": """Create ad copy for {platform} advertising:

Product/Service: {product}
Target audience: {audience}
Campaign goal: {goal}
Budget tier: {budget}

Generate:
- Primary text (compelling hook)
- Headline
- Description
- CTA button text
- 3 ad creative concepts for Canva

Format as JSON."""
}


def get_platform_spec(platform: str) -> dict:
    """Get specifications for a specific platform"""
    return PLATFORM_SPECS.get(platform.lower(), {})


def get_canva_templates(platform: str) -> list:
    """Get Canva template names for a platform"""
    spec = PLATFORM_SPECS.get(platform.lower(), {})
    return spec.get("canva_templates", [])


def get_ai_workflow(workflow_name: str) -> dict:
    """Get an AI design workflow"""
    return AI_DESIGN_WORKFLOWS.get(workflow_name, {})


def get_gemini_prompt(prompt_type: str, **kwargs) -> str:
    """Get a formatted Gemini prompt for design generation"""
    template = GEMINI_DESIGN_PROMPTS.get(prompt_type, "")
    return template.format(**kwargs) if template else ""


def get_all_platforms() -> list:
    """Get list of all supported platforms"""
    return list(PLATFORM_SPECS.keys())


def get_design_tools() -> dict:
    """Get design tools configuration"""
    return DESIGN_TOOLS
