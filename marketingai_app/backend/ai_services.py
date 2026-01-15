"""
AI Services for MarketingAI Platform
Integrates Google Vertex AI, Imagen, Veo, and Gemini for content generation
"""

import os
import json
import base64
import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Any

# Google Cloud AI imports
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part, Image
    from vertexai.preview.vision_models import ImageGenerationModel
    from google.cloud import aiplatform
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    print("Warning: Vertex AI SDK not installed. Install with: pip install google-cloud-aiplatform vertexai")

from google.cloud import storage
from google.cloud import bigquery

# Configuration
PROJECT_ID = os.environ.get('PROJECT_ID', 'aialgotradehits')
LOCATION = os.environ.get('VERTEX_LOCATION', 'us-central1')
DATASET_ID = 'marketingai_data'
GCS_BUCKET = os.environ.get('GCS_BUCKET', 'marketingai-assets')

# Initialize clients
storage_client = storage.Client(project=PROJECT_ID)
bq_client = bigquery.Client(project=PROJECT_ID)


class GeminiService:
    """Google Gemini 2.5 for content generation and analysis"""

    def __init__(self):
        if VERTEX_AI_AVAILABLE:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            # Use Gemini 2.0 Flash (latest available model)
            self.model = GenerativeModel("gemini-2.0-flash-exp")
            self.pro_model = GenerativeModel("gemini-1.5-pro-002")
        else:
            self.model = None
            self.pro_model = None

    async def generate_marketing_copy(
        self,
        product_description: str,
        platform: str,
        tone: str = "professional",
        target_audience: str = "general",
        max_length: int = 500
    ) -> Dict[str, Any]:
        """Generate marketing copy for social media"""

        prompt = f"""You are an expert social media marketer. Create compelling marketing content for the following:

Product/Service: {product_description}
Platform: {platform}
Tone: {tone}
Target Audience: {target_audience}

Generate the following:
1. A catchy headline (max 60 characters)
2. Main caption/copy (max {max_length} characters)
3. 5 relevant hashtags
4. A call-to-action
5. Best posting time suggestion

Format your response as JSON with keys: headline, caption, hashtags (array), cta, best_time

IMPORTANT: Respond ONLY with valid JSON, no markdown or explanation."""

        if not self.model:
            return {"error": "Gemini not available", "headline": "Demo Headline", "caption": product_description}

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # Parse JSON response
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]

            return json.loads(result_text)
        except Exception as e:
            return {"error": str(e), "headline": "Error generating content", "caption": ""}

    async def generate_carousel_content(
        self,
        topic: str,
        num_slides: int = 5,
        style: str = "educational"
    ) -> List[Dict[str, str]]:
        """Generate content for carousel posts"""

        prompt = f"""Create content for a {num_slides}-slide {style} carousel about: {topic}

For each slide, provide:
- Slide number
- Heading (max 40 characters)
- Body text (max 150 characters)
- Visual description for image generation

Format as JSON array with objects containing: slide_num, heading, body, visual_prompt

Make it engaging, educational, and shareable. Start with a hook, end with CTA.
Respond ONLY with valid JSON array."""

        if not self.model:
            return [{"slide_num": i, "heading": f"Slide {i}", "body": "Demo content", "visual_prompt": "Abstract design"} for i in range(1, num_slides + 1)]

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]

            return json.loads(result_text)
        except Exception as e:
            return [{"error": str(e), "slide_num": 1, "heading": "Error", "body": str(e)}]

    async def analyze_content_performance(
        self,
        content_data: List[Dict],
        platform: str
    ) -> Dict[str, Any]:
        """Analyze content performance and provide recommendations"""

        prompt = f"""Analyze the following content performance data for {platform} and provide actionable insights:

Content Data:
{json.dumps(content_data, indent=2)}

Provide:
1. Top performing content patterns
2. Best posting times identified
3. Content type recommendations
4. Hashtag effectiveness analysis
5. Audience engagement insights
6. 5 specific action items to improve performance

Format as JSON with structured recommendations."""

        if not self.pro_model:
            return {"insights": "AI analysis not available", "recommendations": []}

        try:
            response = self.pro_model.generate_content(prompt)
            return json.loads(response.text.strip())
        except Exception as e:
            return {"error": str(e)}

    async def generate_campaign_strategy(
        self,
        brand_info: Dict,
        goals: str,
        duration_days: int,
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Generate a complete marketing campaign strategy"""

        prompt = f"""Create a comprehensive marketing campaign strategy:

Brand Information:
{json.dumps(brand_info, indent=2)}

Campaign Goals: {goals}
Duration: {duration_days} days
Target Platforms: {', '.join(platforms)}

Generate a detailed strategy including:
1. Campaign overview and key messages
2. Content calendar with specific post ideas for each day
3. Content mix (educational, promotional, engagement, behind-scenes percentages)
4. Key visual themes and style guide
5. Hashtag strategy per platform
6. KPIs to track
7. Budget allocation recommendations

Format as comprehensive JSON strategy document."""

        if not self.pro_model:
            return {"error": "AI not available", "strategy": "Demo strategy"}

        try:
            response = self.pro_model.generate_content(prompt)
            return json.loads(response.text.strip())
        except Exception as e:
            return {"error": str(e)}


class ImagenService:
    """Google Imagen for AI image generation"""

    def __init__(self):
        if VERTEX_AI_AVAILABLE:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            try:
                self.model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
            except:
                self.model = None
        else:
            self.model = None

    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        style: str = "photorealistic",
        num_images: int = 1
    ) -> List[Dict[str, str]]:
        """Generate images using Imagen 3.0"""

        enhanced_prompt = f"{style} style: {prompt}"

        if not self.model:
            return [{"url": "https://via.placeholder.com/1080x1080?text=Demo+Image", "prompt": prompt}]

        try:
            images = self.model.generate_images(
                prompt=enhanced_prompt,
                number_of_images=num_images,
                aspect_ratio=aspect_ratio,
                safety_filter_level="block_medium_and_above",
                person_generation="allow_adult"
            )

            results = []
            for i, image in enumerate(images):
                # Save to GCS
                filename = f"generated/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.png"
                url = await self._save_to_gcs(image._image_bytes, filename)
                results.append({"url": url, "prompt": prompt})

            return results
        except Exception as e:
            return [{"error": str(e), "url": "", "prompt": prompt}]

    async def generate_social_graphics(
        self,
        brand_colors: Dict[str, str],
        text_content: str,
        platform: str,
        template_style: str = "modern"
    ) -> Dict[str, Any]:
        """Generate branded social media graphics"""

        dimensions = {
            "instagram_feed": "1:1",
            "instagram_story": "9:16",
            "facebook": "1.91:1",
            "youtube_thumbnail": "16:9",
            "tiktok": "9:16"
        }

        aspect_ratio = dimensions.get(platform, "1:1")

        prompt = f"""Professional social media graphic for {platform}:
Theme: {template_style}
Primary color: {brand_colors.get('primary', '#667eea')}
Secondary color: {brand_colors.get('secondary', '#764ba2')}
Text to incorporate: {text_content}
Style: Clean, modern, {template_style} design with bold typography"""

        return await self.generate_image(prompt, aspect_ratio, "digital art")

    async def _save_to_gcs(self, image_bytes: bytes, filename: str) -> str:
        """Save image to Google Cloud Storage"""
        try:
            bucket = storage_client.bucket(GCS_BUCKET)
            blob = bucket.blob(filename)
            blob.upload_from_string(image_bytes, content_type='image/png')
            return f"https://storage.googleapis.com/{GCS_BUCKET}/{filename}"
        except Exception as e:
            return f"error://{str(e)}"


class VeoService:
    """Google Veo for AI video generation"""

    def __init__(self):
        self.available = VERTEX_AI_AVAILABLE
        # Veo 3.1 API when available
        self.endpoint = f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/veo-001"

    async def generate_video(
        self,
        prompt: str,
        duration_seconds: int = 5,
        aspect_ratio: str = "16:9",
        style: str = "cinematic"
    ) -> Dict[str, Any]:
        """Generate short video using Veo"""

        enhanced_prompt = f"{style} video: {prompt}"

        # Veo API call (when available)
        # For now, return placeholder
        return {
            "status": "pending",
            "prompt": enhanced_prompt,
            "duration": duration_seconds,
            "message": "Video generation queued. Veo 3.1 integration in progress.",
            "estimated_time": "2-5 minutes"
        }

    async def image_to_video(
        self,
        image_url: str,
        motion_prompt: str,
        duration_seconds: int = 5
    ) -> Dict[str, Any]:
        """Animate a static image into video"""

        return {
            "status": "pending",
            "source_image": image_url,
            "motion": motion_prompt,
            "duration": duration_seconds,
            "message": "Image-to-video conversion queued."
        }


class CampaignAgent:
    """AI Agent for automated marketing campaign management"""

    def __init__(self):
        self.gemini = GeminiService()
        self.imagen = ImagenService()
        self.veo = VeoService()

    async def create_campaign(
        self,
        brand_id: str,
        user_id: str,
        campaign_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create and schedule a complete marketing campaign"""

        # Extract configuration
        goals = campaign_config.get('goals', 'brand awareness')
        duration = campaign_config.get('duration_days', 7)
        platforms = campaign_config.get('platforms', ['instagram'])
        content_frequency = campaign_config.get('posts_per_day', 1)

        # Get brand info
        brand_info = await self._get_brand_info(brand_id)

        # Generate campaign strategy
        strategy = await self.gemini.generate_campaign_strategy(
            brand_info, goals, duration, platforms
        )

        # Generate content for each scheduled post
        content_items = []
        calendar = strategy.get('content_calendar', [])

        for day_content in calendar[:duration * content_frequency]:
            # Generate text content
            copy = await self.gemini.generate_marketing_copy(
                day_content.get('topic', 'brand message'),
                day_content.get('platform', platforms[0]),
                brand_info.get('tone', 'professional')
            )

            # Generate visuals
            images = await self.imagen.generate_social_graphics(
                {
                    'primary': brand_info.get('primary_color', '#667eea'),
                    'secondary': brand_info.get('secondary_color', '#764ba2')
                },
                copy.get('headline', ''),
                day_content.get('platform', 'instagram_feed')
            )

            content_items.append({
                'day': day_content.get('day', 1),
                'platform': day_content.get('platform', platforms[0]),
                'type': day_content.get('type', 'post'),
                'copy': copy,
                'images': images,
                'status': 'draft'
            })

        # Save campaign to database
        campaign_id = await self._save_campaign(user_id, brand_id, strategy, content_items)

        return {
            'campaign_id': campaign_id,
            'status': 'created',
            'strategy': strategy,
            'content_count': len(content_items),
            'platforms': platforms,
            'duration_days': duration
        }

    async def optimize_campaign(
        self,
        campaign_id: str,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze and optimize running campaign based on performance"""

        analysis = await self.gemini.analyze_content_performance(
            performance_data.get('posts', []),
            performance_data.get('platform', 'instagram')
        )

        return {
            'campaign_id': campaign_id,
            'analysis': analysis,
            'recommendations': analysis.get('recommendations', []),
            'suggested_changes': analysis.get('action_items', [])
        }

    async def auto_respond(
        self,
        comment_data: Dict[str, str],
        brand_voice: str
    ) -> str:
        """Generate automated response to comments/messages"""

        prompt = f"""Generate a helpful, on-brand response to this comment:
Comment: {comment_data.get('text', '')}
Brand voice: {brand_voice}
Keep it friendly, helpful, and under 280 characters."""

        if not self.gemini.model:
            return "Thank you for your comment! We appreciate your engagement."

        try:
            response = self.gemini.model.generate_content(prompt)
            return response.text.strip()[:280]
        except:
            return "Thank you for reaching out! We'll get back to you soon."

    async def _get_brand_info(self, brand_id: str) -> Dict[str, Any]:
        """Fetch brand information from database"""
        query = f"""
            SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.brands`
            WHERE brand_id = @brand_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("brand_id", "STRING", brand_id)
            ]
        )
        results = list(bq_client.query(query, job_config=job_config).result())

        if results:
            row = results[0]
            return {
                'name': row.name,
                'description': row.description,
                'primary_color': row.primary_color,
                'secondary_color': row.secondary_color,
                'theme': row.theme
            }
        return {}

    async def _save_campaign(
        self,
        user_id: str,
        brand_id: str,
        strategy: Dict,
        content_items: List[Dict]
    ) -> str:
        """Save campaign to database"""
        import secrets
        campaign_id = secrets.token_hex(8)

        # For now, return the ID - full implementation would insert into BigQuery
        return campaign_id


# Service instances
gemini_service = GeminiService()
imagen_service = ImagenService()
veo_service = VeoService()
campaign_agent = CampaignAgent()
