"""
MarketingAI - Gemini 2.5 Integration
Text and multimodal content generation for marketing
"""
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from google.cloud import aiplatform
from google.cloud import bigquery

# Initialize Vertex AI
PROJECT_ID = os.environ.get('PROJECT_ID', 'aialgotradehits')
LOCATION = 'us-central1'

try:
    aiplatform.init(project=PROJECT_ID, location=LOCATION)
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    GEMINI_AVAILABLE = True
except Exception as e:
    print(f"Gemini initialization warning: {e}")
    GEMINI_AVAILABLE = False


class GeminiContentGenerator:
    """
    AI content generation using Google Gemini 2.5 Pro/Flash
    Generates marketing content: social posts, blogs, emails, ads
    """

    def __init__(self):
        self.project_id = PROJECT_ID
        self.location = LOCATION

        if GEMINI_AVAILABLE:
            # Use Gemini 2.5 Pro for complex reasoning tasks
            self.pro_model = GenerativeModel("gemini-2.5-pro")
            # Use Gemini 2.5 Flash for fast generation
            self.flash_model = GenerativeModel("gemini-2.5-flash")
        else:
            self.pro_model = None
            self.flash_model = None

        # BigQuery client for logging
        try:
            self.bq_client = bigquery.Client(project=PROJECT_ID)
        except:
            self.bq_client = None

    # ==================== SOCIAL MEDIA CONTENT ====================

    async def generate_social_post(
        self,
        prompt: str,
        platform: str,
        tone: str = "professional",
        brand_voice: str = "",
        target_audience: str = "",
        include_hashtags: bool = True,
        include_emojis: bool = True
    ) -> Dict[str, Any]:
        """
        Generate platform-optimized social media post

        Args:
            prompt: Content topic or description
            platform: instagram, facebook, linkedin, twitter, tiktok
            tone: professional, casual, humorous, inspiring
            brand_voice: Brand personality description
            target_audience: Target demographic
            include_hashtags: Add relevant hashtags
            include_emojis: Add emojis

        Returns:
            Dict with text, hashtags, image_prompt, posting_time
        """
        if not GEMINI_AVAILABLE:
            return {"error": "Gemini not available", "success": False}

        platform_specs = self._get_platform_specs(platform)

        system_prompt = f"""You are an expert social media marketer creating content for {platform}.

Brand Voice: {brand_voice if brand_voice else "Professional and engaging"}
Tone: {tone}
Target Audience: {target_audience if target_audience else "General audience"}

Platform Requirements for {platform}:
- Maximum characters: {platform_specs['max_chars']}
- Optimal hashtag count: {platform_specs['hashtags']}
- Best practices: {platform_specs['best_practices']}
- Content style: {platform_specs['content_style']}

Guidelines:
- Create authentic, engaging content that drives action
- {"Include relevant, trending hashtags" if include_hashtags else "Do NOT include hashtags"}
- {"Use appropriate emojis to increase engagement" if include_emojis else "Do NOT use emojis"}
- Include a clear call-to-action when appropriate
- Optimize for the platform's algorithm

Respond in valid JSON format:
{{
    "text": "The full post text optimized for {platform}",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
    "suggested_image_prompt": "Detailed image description for AI image generation",
    "best_posting_time": "Day and time recommendation",
    "engagement_prediction": "high/medium/low",
    "content_type": "educational/promotional/entertaining/inspirational",
    "hook": "The attention-grabbing first line"
}}
"""

        try:
            response = await self.flash_model.generate_content_async(
                contents=[system_prompt, f"Create a post about: {prompt}"],
                generation_config=GenerationConfig(
                    temperature=0.8,
                    top_p=0.95,
                    max_output_tokens=2048,
                    response_mime_type="application/json"
                )
            )

            result = self._parse_json_response(response)
            result['success'] = True
            result['platform'] = platform
            result['model_used'] = 'gemini-2.5-flash'

            return result

        except Exception as e:
            return {"error": str(e), "success": False}

    async def generate_content_calendar(
        self,
        days: int,
        platforms: List[str],
        brand_voice: str,
        content_pillars: List[str],
        posting_frequency: str = "daily"
    ) -> Dict[str, Any]:
        """
        Generate a complete content calendar for multiple platforms

        Args:
            days: Number of days to plan
            platforms: List of platforms
            brand_voice: Brand personality
            content_pillars: Main content themes
            posting_frequency: daily, twice_daily, every_other_day

        Returns:
            Dict with calendar entries
        """
        if not GEMINI_AVAILABLE:
            return {"error": "Gemini not available", "success": False}

        system_prompt = f"""You are a content strategist creating a {days}-day content calendar.

Brand Voice: {brand_voice}
Platforms: {', '.join(platforms)}
Content Pillars: {', '.join(content_pillars)}
Posting Frequency: {posting_frequency}

Create a diverse, engaging content calendar that:
- Balances content types (educational, promotional, entertaining, inspirational)
- Includes platform-specific optimizations
- Has strong hooks and CTAs
- Maintains brand consistency
- Optimizes posting times for each platform

Respond in valid JSON format:
{{
    "calendar": [
        {{
            "day": 1,
            "date": "Day 1",
            "posts": [
                {{
                    "platform": "instagram",
                    "content_type": "educational",
                    "pillar": "content pillar name",
                    "text": "Full post text",
                    "hashtags": ["tag1", "tag2"],
                    "image_prompt": "Image description",
                    "posting_time": "9:00 AM EST",
                    "hook": "Attention grabber"
                }}
            ]
        }}
    ],
    "total_posts": number,
    "content_mix": {{
        "educational": percentage,
        "promotional": percentage,
        "entertaining": percentage,
        "inspirational": percentage
    }}
}}
"""

        try:
            response = await self.pro_model.generate_content_async(
                contents=[system_prompt],
                generation_config=GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=8192,
                    response_mime_type="application/json"
                )
            )

            result = self._parse_json_response(response)
            result['success'] = True
            result['model_used'] = 'gemini-2.5-pro'

            return result

        except Exception as e:
            return {"error": str(e), "success": False}

    # ==================== BLOG ARTICLES ====================

    async def generate_blog_article(
        self,
        topic: str,
        keywords: List[str] = None,
        word_count: int = 1500,
        tone: str = "informative",
        seo_optimize: bool = True,
        include_sections: bool = True
    ) -> Dict[str, Any]:
        """
        Generate SEO-optimized blog article

        Args:
            topic: Article topic
            keywords: Target SEO keywords
            word_count: Target word count
            tone: Writing tone
            seo_optimize: Include SEO elements
            include_sections: Add headers/sections

        Returns:
            Dict with title, meta, content, headers
        """
        if not GEMINI_AVAILABLE:
            return {"error": "Gemini not available", "success": False}

        keywords_str = ', '.join(keywords) if keywords else 'auto-detect'

        system_prompt = f"""You are an expert content writer creating a blog article.

Topic: {topic}
Target Keywords: {keywords_str}
Target Word Count: {word_count}
Tone: {tone}
SEO Optimization: {"Yes - naturally incorporate keywords, use header hierarchy, meta description" if seo_optimize else "No"}

Article Requirements:
- Compelling, click-worthy title (under 60 chars for SEO)
- Engaging introduction that hooks readers
- Well-structured with H2/H3 headers
- Actionable insights and takeaways
- Natural keyword integration
- Strong conclusion with CTA
- Readable formatting with short paragraphs

Respond in valid JSON format:
{{
    "title": "SEO-optimized title under 60 characters",
    "meta_description": "Compelling 155-character meta description with primary keyword",
    "slug": "url-friendly-slug",
    "introduction": "Hook paragraph",
    "sections": [
        {{
            "header": "H2 Section Header",
            "content": "Section content with markdown formatting",
            "subsections": [
                {{
                    "header": "H3 Subsection",
                    "content": "Subsection content"
                }}
            ]
        }}
    ],
    "conclusion": "Strong conclusion with CTA",
    "full_content": "Complete article in markdown format",
    "word_count": actual_count,
    "keywords_used": ["keyword1", "keyword2"],
    "readability_score": "grade level estimate",
    "suggested_images": [
        {{
            "section": "section name",
            "prompt": "AI image generation prompt",
            "alt_text": "SEO-friendly alt text"
        }}
    ],
    "internal_linking_opportunities": ["topic1", "topic2"],
    "cta": "Call to action text"
}}
"""

        try:
            response = await self.pro_model.generate_content_async(
                contents=[system_prompt],
                generation_config=GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=8192,
                    response_mime_type="application/json"
                )
            )

            result = self._parse_json_response(response)
            result['success'] = True
            result['model_used'] = 'gemini-2.5-pro'

            return result

        except Exception as e:
            return {"error": str(e), "success": False}

    # ==================== EMAIL CAMPAIGNS ====================

    async def generate_email_campaign(
        self,
        campaign_goal: str,
        audience_segment: str,
        brand_voice: str = "",
        cta: str = "",
        email_type: str = "promotional",
        personalization_fields: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate email campaign with subject lines, body, and CTAs

        Args:
            campaign_goal: Objective (sales, awareness, engagement)
            audience_segment: Target audience description
            brand_voice: Brand personality
            cta: Primary call to action
            email_type: promotional, newsletter, welcome, abandoned_cart
            personalization_fields: Fields to personalize

        Returns:
            Dict with subject lines, preview text, body, CTAs
        """
        if not GEMINI_AVAILABLE:
            return {"error": "Gemini not available", "success": False}

        personalization = personalization_fields or ['first_name']

        system_prompt = f"""You are an expert email marketer creating a {email_type} email campaign.

Campaign Goal: {campaign_goal}
Audience Segment: {audience_segment}
Brand Voice: {brand_voice if brand_voice else "Professional and friendly"}
Primary CTA: {cta if cta else "Learn More"}
Email Type: {email_type}
Personalization Fields Available: {', '.join(personalization)}

Email Best Practices:
- Subject lines: 30-50 chars, create urgency/curiosity
- Preview text: Complement subject line, 40-100 chars
- Body: Clear, scannable, mobile-friendly
- Single primary CTA (can have secondary)
- Personalization increases open rates 26%

Respond in valid JSON format:
{{
    "subject_lines": [
        {{
            "text": "Subject line 1",
            "type": "curiosity/urgency/benefit/personalized",
            "predicted_open_rate": "percentage"
        }},
        {{
            "text": "Subject line 2",
            "type": "type",
            "predicted_open_rate": "percentage"
        }}
    ],
    "preview_text": "Email preview text",
    "body_html": "Full HTML email body with {{{{first_name}}}} personalization",
    "body_plain": "Plain text version",
    "primary_cta": {{
        "text": "Button text",
        "url_placeholder": "{{{{cta_url}}}}"
    }},
    "secondary_cta": {{
        "text": "Secondary action",
        "url_placeholder": "{{{{secondary_url}}}}"
    }},
    "send_time_recommendation": {{
        "day": "Best day",
        "time": "Best time",
        "timezone": "EST",
        "reasoning": "Why this time"
    }},
    "a_b_test_suggestions": [
        {{
            "element": "subject_line",
            "variant_a": "Option A",
            "variant_b": "Option B"
        }}
    ],
    "segmentation_tips": ["tip1", "tip2"]
}}
"""

        try:
            response = await self.pro_model.generate_content_async(
                contents=[system_prompt],
                generation_config=GenerationConfig(
                    temperature=0.8,
                    max_output_tokens=4096,
                    response_mime_type="application/json"
                )
            )

            result = self._parse_json_response(response)
            result['success'] = True
            result['model_used'] = 'gemini-2.5-pro'
            result['email_type'] = email_type

            return result

        except Exception as e:
            return {"error": str(e), "success": False}

    # ==================== AD COPY ====================

    async def generate_ad_copy(
        self,
        product: str,
        platform: str,
        ad_format: str = "feed",
        target_audience: str = "",
        budget: float = 100,
        goal: str = "conversions",
        unique_selling_points: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate high-converting ad copy

        Args:
            product: Product/service description
            platform: google, facebook, instagram, linkedin, tiktok
            ad_format: feed, story, search, display, video
            target_audience: Target demographic
            budget: Daily budget
            goal: conversions, traffic, awareness, leads
            unique_selling_points: Key differentiators

        Returns:
            Dict with headlines, descriptions, CTAs, targeting
        """
        if not GEMINI_AVAILABLE:
            return {"error": "Gemini not available", "success": False}

        ad_specs = self._get_ad_specs(platform, ad_format)
        usps = unique_selling_points or []

        system_prompt = f"""You are an expert digital advertiser creating {ad_format} ads for {platform}.

Product/Service: {product}
Unique Selling Points: {', '.join(usps) if usps else 'To be identified'}
Target Audience: {target_audience}
Campaign Goal: {goal}
Daily Budget: ${budget}

Ad Specifications for {platform} {ad_format}:
- Headline maximum: {ad_specs['headline_max']} characters
- Description maximum: {ad_specs['description_max']} characters
- Available CTAs: {', '.join(ad_specs['cta_options'])}
- Image specs: {ad_specs.get('image_specs', 'Standard')}

Create multiple variations for A/B testing.

Respond in valid JSON format:
{{
    "headlines": [
        {{
            "text": "Headline text",
            "char_count": number,
            "angle": "benefit/feature/social_proof/urgency"
        }}
    ],
    "descriptions": [
        {{
            "text": "Description text",
            "char_count": number,
            "focus": "what aspect it emphasizes"
        }}
    ],
    "primary_text": [
        {{
            "text": "Primary text for feed ads",
            "hook": "Opening hook"
        }}
    ],
    "ctas": ["CTA1", "CTA2"],
    "image_prompts": [
        {{
            "prompt": "AI image generation prompt",
            "style": "lifestyle/product/graphic",
            "specs": "{ad_specs.get('image_specs', '1:1')}"
        }}
    ],
    "targeting_recommendations": {{
        "demographics": {{
            "age_range": "25-54",
            "gender": "all/male/female",
            "locations": ["US", "CA"]
        }},
        "interests": ["interest1", "interest2"],
        "behaviors": ["behavior1", "behavior2"],
        "custom_audiences": ["suggestion1", "suggestion2"],
        "lookalike_seed": "Best audience to model"
    }},
    "budget_allocation": {{
        "daily_budget": {budget},
        "bid_strategy": "recommended strategy",
        "optimization_goal": "{goal}"
    }},
    "ad_schedule": {{
        "best_days": ["Monday", "Tuesday"],
        "best_hours": "9AM-6PM",
        "reasoning": "Why"
    }}
}}
"""

        try:
            response = await self.flash_model.generate_content_async(
                contents=[system_prompt],
                generation_config=GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=4096,
                    response_mime_type="application/json"
                )
            )

            result = self._parse_json_response(response)
            result['success'] = True
            result['model_used'] = 'gemini-2.5-flash'
            result['platform'] = platform
            result['ad_format'] = ad_format

            return result

        except Exception as e:
            return {"error": str(e), "success": False}

    # ==================== VIDEO SCRIPTS ====================

    async def generate_video_script(
        self,
        topic: str,
        platform: str,
        duration: int = 60,
        style: str = "educational",
        include_hooks: bool = True
    ) -> Dict[str, Any]:
        """
        Generate video script for social media

        Args:
            topic: Video topic
            platform: tiktok, instagram_reel, youtube_short, youtube
            duration: Target duration in seconds
            style: educational, entertaining, promotional, storytelling
            include_hooks: Include attention hooks

        Returns:
            Dict with script, scenes, hooks, CTAs
        """
        if not GEMINI_AVAILABLE:
            return {"error": "Gemini not available", "success": False}

        platform_specs = {
            "tiktok": {"max_duration": 180, "aspect": "9:16", "hooks_crucial": True},
            "instagram_reel": {"max_duration": 90, "aspect": "9:16", "hooks_crucial": True},
            "youtube_short": {"max_duration": 60, "aspect": "9:16", "hooks_crucial": True},
            "youtube": {"max_duration": 600, "aspect": "16:9", "hooks_crucial": False}
        }

        spec = platform_specs.get(platform, platform_specs["tiktok"])

        system_prompt = f"""You are a viral video scriptwriter creating a {platform} video.

Topic: {topic}
Duration: {min(duration, spec['max_duration'])} seconds
Style: {style}
Aspect Ratio: {spec['aspect']}

Platform-Specific Requirements:
- Hook viewers in first 3 seconds (critical for {platform})
- Optimize for {spec['aspect']} vertical/horizontal viewing
- Include pattern interrupts to maintain attention
- End with clear CTA
- Consider trending audio/effects

Respond in valid JSON format:
{{
    "title": "Video title",
    "hook": {{
        "text": "Opening hook (first 3 seconds)",
        "visual": "What viewers see",
        "audio": "What viewers hear"
    }},
    "script": {{
        "full_text": "Complete spoken script",
        "word_count": number,
        "estimated_duration": "X seconds"
    }},
    "scenes": [
        {{
            "scene_number": 1,
            "duration": "X seconds",
            "spoken_text": "What's said",
            "visual_description": "What's shown",
            "text_overlay": "On-screen text",
            "transition": "Cut/fade/swipe"
        }}
    ],
    "cta": {{
        "text": "Call to action",
        "timing": "When it appears",
        "visual": "How it's shown"
    }},
    "suggested_audio": {{
        "type": "trending/original/voiceover",
        "description": "Audio suggestion"
    }},
    "hashtags": ["relevant", "hashtags"],
    "caption": "Video caption/description",
    "thumbnail_prompt": "AI image prompt for thumbnail"
}}
"""

        try:
            response = await self.flash_model.generate_content_async(
                contents=[system_prompt],
                generation_config=GenerationConfig(
                    temperature=0.8,
                    max_output_tokens=4096,
                    response_mime_type="application/json"
                )
            )

            result = self._parse_json_response(response)
            result['success'] = True
            result['model_used'] = 'gemini-2.5-flash'
            result['platform'] = platform

            return result

        except Exception as e:
            return {"error": str(e), "success": False}

    # ==================== HELPER METHODS ====================

    def _get_platform_specs(self, platform: str) -> Dict:
        """Get platform-specific specifications"""
        specs = {
            "instagram": {
                "max_chars": 2200,
                "hashtags": "20-30 (mix of popular and niche)",
                "best_practices": "Visual-first, carousel for engagement, Reels for reach",
                "content_style": "Aesthetic, lifestyle-focused, behind-the-scenes"
            },
            "facebook": {
                "max_chars": 63206,
                "hashtags": "1-3 (less emphasis on hashtags)",
                "best_practices": "Native video, questions for engagement, link in comments",
                "content_style": "Community-focused, shareable, discussion-sparking"
            },
            "linkedin": {
                "max_chars": 3000,
                "hashtags": "3-5 (industry and topic relevant)",
                "best_practices": "Professional tone, thought leadership, document posts",
                "content_style": "Educational, industry insights, career-focused"
            },
            "twitter": {
                "max_chars": 280,
                "hashtags": "1-2 (trending when relevant)",
                "best_practices": "Threads for engagement, polls, timely content, replies",
                "content_style": "Conversational, witty, news-jacking"
            },
            "tiktok": {
                "max_chars": 2200,
                "hashtags": "3-5 (trending + niche)",
                "best_practices": "Trends, hooks in first 3 seconds, vertical video, duets",
                "content_style": "Authentic, entertaining, trend-driven"
            },
            "youtube": {
                "max_chars": 5000,
                "hashtags": "3-5 (in description)",
                "best_practices": "SEO titles, thumbnails, chapters, cards/end screens",
                "content_style": "Educational, entertaining, long-form value"
            },
            "pinterest": {
                "max_chars": 500,
                "hashtags": "2-5",
                "best_practices": "Vertical images, keyword-rich descriptions, idea pins",
                "content_style": "Inspirational, how-to, visual tutorials"
            }
        }
        return specs.get(platform.lower(), specs["instagram"])

    def _get_ad_specs(self, platform: str, ad_format: str) -> Dict:
        """Get ad specifications by platform and format"""
        specs = {
            "google": {
                "headline_max": 30,
                "description_max": 90,
                "cta_options": ["Shop Now", "Learn More", "Get Started", "Sign Up", "Contact Us"],
                "image_specs": "1200x628 landscape"
            },
            "facebook": {
                "headline_max": 40,
                "description_max": 125,
                "cta_options": ["Shop Now", "Learn More", "Sign Up", "Contact Us", "Book Now", "Download"],
                "image_specs": "1080x1080 or 1080x1350"
            },
            "instagram": {
                "headline_max": 40,
                "description_max": 125,
                "cta_options": ["Shop Now", "Learn More", "Sign Up", "Watch More", "Book Now"],
                "image_specs": "1080x1080 feed, 1080x1920 story"
            },
            "linkedin": {
                "headline_max": 70,
                "description_max": 100,
                "cta_options": ["Learn More", "Sign Up", "Register", "Download", "Apply Now"],
                "image_specs": "1200x627"
            },
            "tiktok": {
                "headline_max": 100,
                "description_max": 100,
                "cta_options": ["Shop Now", "Learn More", "Sign Up", "Download", "Contact Us"],
                "image_specs": "1080x1920 vertical video"
            }
        }
        return specs.get(platform.lower(), specs["facebook"])

    def _parse_json_response(self, response) -> Dict:
        """Parse JSON response from Gemini"""
        try:
            text = response.text
            # Clean up potential markdown code blocks
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            return {
                "raw_text": response.text,
                "parse_error": str(e),
                "success": False
            }

    # ==================== LOGGING ====================

    def log_generation(
        self,
        user_id: str,
        generation_type: str,
        prompt: str,
        result: Dict,
        model_used: str
    ):
        """Log AI generation to BigQuery for analytics"""
        if not self.bq_client:
            return

        try:
            table_id = f"{PROJECT_ID}.marketingai_data.ai_generations"
            row = {
                "generation_id": f"gen_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
                "user_id": user_id,
                "generation_type": generation_type,
                "model_used": model_used,
                "prompt": prompt[:1000],  # Truncate long prompts
                "result": json.dumps(result)[:5000],  # Truncate long results
                "success": result.get('success', False),
                "created_at": datetime.utcnow().isoformat()
            }

            errors = self.bq_client.insert_rows_json(table_id, [row])
            if errors:
                print(f"BigQuery logging error: {errors}")
        except Exception as e:
            print(f"Logging error: {e}")


# ==================== SINGLETON INSTANCE ====================

_generator_instance = None

def get_gemini_generator() -> GeminiContentGenerator:
    """Get singleton instance of GeminiContentGenerator"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = GeminiContentGenerator()
    return _generator_instance
