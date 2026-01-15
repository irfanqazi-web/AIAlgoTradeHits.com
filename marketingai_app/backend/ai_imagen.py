"""
MarketingAI - Imagen 4 Integration
AI-powered image generation for marketing visuals
"""
import os
import json
import base64
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from google.cloud import storage
from google.cloud import bigquery

# Initialize Vertex AI
PROJECT_ID = os.environ.get('PROJECT_ID', 'aialgotradehits')
LOCATION = 'us-central1'
BUCKET_NAME = 'aialgotradehits-marketing-images'

try:
    from vertexai.preview.vision_models import ImageGenerationModel, Image
    IMAGEN_AVAILABLE = True
except ImportError:
    IMAGEN_AVAILABLE = False
    print("Imagen SDK not available - install vertexai package")


class ImagenGenerator:
    """
    AI image generation using Google Imagen 4
    Creates marketing visuals: social graphics, product images, ads
    """

    def __init__(self):
        self.project_id = PROJECT_ID
        self.location = LOCATION
        self.bucket_name = BUCKET_NAME

        if IMAGEN_AVAILABLE:
            # Imagen 4 model ID
            self.model = ImageGenerationModel.from_pretrained("imagen-4.0-generate-preview-05-20")
        else:
            self.model = None

        # Storage client for saving images
        try:
            self.storage_client = storage.Client(project=PROJECT_ID)
            self.bucket = self.storage_client.bucket(BUCKET_NAME)
        except Exception as e:
            print(f"Storage client warning: {e}")
            self.storage_client = None
            self.bucket = None

        # BigQuery for logging
        try:
            self.bq_client = bigquery.Client(project=PROJECT_ID)
        except:
            self.bq_client = None

    # ==================== SOCIAL MEDIA GRAPHICS ====================

    async def generate_social_graphic(
        self,
        prompt: str,
        platform: str,
        style: str = "professional",
        brand_colors: List[str] = None,
        include_text_space: bool = True,
        aspect_ratio: str = None,
        num_images: int = 4
    ) -> Dict[str, Any]:
        """
        Generate social media graphic optimized for platform

        Args:
            prompt: Image description
            platform: instagram, facebook, linkedin, twitter, pinterest, tiktok
            style: professional, playful, minimalist, bold, vintage
            brand_colors: Hex colors to incorporate
            include_text_space: Leave space for text overlay
            aspect_ratio: Override default aspect ratio
            num_images: Number of variations (1-8)

        Returns:
            Dict with image URLs, prompts, metadata
        """
        if not IMAGEN_AVAILABLE or not self.model:
            return {"error": "Imagen not available", "success": False}

        # Platform-specific dimensions
        platform_specs = {
            "instagram": {"aspect": "1:1", "size": "1080x1080", "alt": "4:5"},
            "instagram_story": {"aspect": "9:16", "size": "1080x1920"},
            "facebook": {"aspect": "1:1", "size": "1200x1200", "alt": "16:9"},
            "linkedin": {"aspect": "1.91:1", "size": "1200x627"},
            "twitter": {"aspect": "16:9", "size": "1200x675"},
            "pinterest": {"aspect": "2:3", "size": "1000x1500"},
            "tiktok": {"aspect": "9:16", "size": "1080x1920"},
            "youtube_thumbnail": {"aspect": "16:9", "size": "1280x720"}
        }

        spec = platform_specs.get(platform.lower(), platform_specs["instagram"])
        target_aspect = aspect_ratio or spec["aspect"]

        # Build enhanced prompt
        color_guidance = ""
        if brand_colors:
            color_guidance = f"Color palette: {', '.join(brand_colors)}. "

        text_space = "Leave clean space at bottom or center for text overlay. " if include_text_space else ""

        style_guidance = {
            "professional": "Clean, corporate, sophisticated lighting, high-end feel",
            "playful": "Bright, fun, energetic, dynamic composition",
            "minimalist": "Simple, clean lines, lots of negative space, elegant",
            "bold": "Strong colors, high contrast, dramatic, eye-catching",
            "vintage": "Warm tones, nostalgic, film-like, classic aesthetics",
            "modern": "Contemporary, sleek, trendy, cutting-edge design"
        }

        enhanced_prompt = f"""
{prompt}

Style: {style_guidance.get(style, style_guidance['professional'])}
{color_guidance}
{text_space}
Aspect ratio: {target_aspect}
High quality, professional marketing image, suitable for {platform}.
Sharp, well-lit, commercially polished.
"""

        try:
            # Generate images
            images = self.model.generate_images(
                prompt=enhanced_prompt.strip(),
                number_of_images=min(num_images, 8),
                aspect_ratio=target_aspect,
                safety_filter_level="block_some",
                person_generation="allow_adult"
            )

            # Save to Cloud Storage and collect URLs
            image_results = []
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

            for i, image in enumerate(images):
                filename = f"social/{platform}/{timestamp}_{i}.png"

                if self.bucket:
                    # Save to Cloud Storage
                    blob = self.bucket.blob(filename)
                    blob.upload_from_string(
                        image._image_bytes,
                        content_type='image/png'
                    )
                    blob.make_public()
                    url = blob.public_url
                else:
                    # Return base64 if no storage
                    url = f"data:image/png;base64,{base64.b64encode(image._image_bytes).decode()}"

                image_results.append({
                    "url": url,
                    "filename": filename,
                    "index": i,
                    "aspect_ratio": target_aspect
                })

            return {
                "success": True,
                "images": image_results,
                "prompt_used": enhanced_prompt.strip(),
                "platform": platform,
                "style": style,
                "aspect_ratio": target_aspect,
                "model": "imagen-4.0-generate-preview-05-20"
            }

        except Exception as e:
            return {"error": str(e), "success": False}

    # ==================== PRODUCT IMAGES ====================

    async def generate_product_image(
        self,
        product_description: str,
        background: str = "studio",
        angle: str = "hero",
        lighting: str = "soft",
        props: List[str] = None,
        aspect_ratio: str = "1:1"
    ) -> Dict[str, Any]:
        """
        Generate professional product photography

        Args:
            product_description: What the product is
            background: studio, lifestyle, flat_lay, gradient, scene
            angle: hero, overhead, side, three_quarter, detail
            lighting: soft, dramatic, natural, bright, moody
            props: Additional elements to include
            aspect_ratio: Image aspect ratio

        Returns:
            Dict with image URLs and metadata
        """
        if not IMAGEN_AVAILABLE or not self.model:
            return {"error": "Imagen not available", "success": False}

        background_styles = {
            "studio": "Clean white studio backdrop, seamless background",
            "lifestyle": "Lifestyle setting showing product in use, contextual environment",
            "flat_lay": "Top-down flat lay arrangement on neutral surface",
            "gradient": "Smooth gradient background, modern and clean",
            "scene": "Styled scene with complementary elements",
            "nature": "Natural outdoor setting, organic feel"
        }

        angle_styles = {
            "hero": "Hero shot, main product angle, 3/4 view",
            "overhead": "Top-down bird's eye view",
            "side": "Profile side view",
            "three_quarter": "Dynamic 3/4 angle showing dimension",
            "detail": "Close-up macro detail shot",
            "front": "Straight-on front facing view"
        }

        lighting_styles = {
            "soft": "Soft, diffused lighting, minimal shadows",
            "dramatic": "High contrast, dramatic shadows, moody",
            "natural": "Natural daylight, window light feel",
            "bright": "Bright, even lighting, commercial feel",
            "moody": "Low key, atmospheric, artistic shadows"
        }

        props_text = f"Include props: {', '.join(props)}. " if props else ""

        enhanced_prompt = f"""
Professional product photography of {product_description}

Background: {background_styles.get(background, background_styles['studio'])}
Angle: {angle_styles.get(angle, angle_styles['hero'])}
Lighting: {lighting_styles.get(lighting, lighting_styles['soft'])}
{props_text}

High-end commercial product photography quality.
Sharp focus on product, professional composition.
Suitable for e-commerce and marketing materials.
8K quality, photorealistic, professional studio look.
"""

        try:
            images = self.model.generate_images(
                prompt=enhanced_prompt.strip(),
                number_of_images=4,
                aspect_ratio=aspect_ratio,
                safety_filter_level="block_some"
            )

            image_results = []
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

            for i, image in enumerate(images):
                filename = f"products/{timestamp}_{i}.png"

                if self.bucket:
                    blob = self.bucket.blob(filename)
                    blob.upload_from_string(
                        image._image_bytes,
                        content_type='image/png'
                    )
                    blob.make_public()
                    url = blob.public_url
                else:
                    url = f"data:image/png;base64,{base64.b64encode(image._image_bytes).decode()}"

                image_results.append({
                    "url": url,
                    "filename": filename,
                    "index": i
                })

            return {
                "success": True,
                "images": image_results,
                "prompt_used": enhanced_prompt.strip(),
                "background": background,
                "angle": angle,
                "lighting": lighting,
                "model": "imagen-4.0-generate-preview-05-20"
            }

        except Exception as e:
            return {"error": str(e), "success": False}

    # ==================== AD CREATIVES ====================

    async def generate_ad_creative(
        self,
        product: str,
        ad_type: str = "display",
        message: str = "",
        cta: str = "",
        brand_elements: Dict = None,
        sizes: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate ad creative images

        Args:
            product: Product/service being advertised
            ad_type: display, social, banner, carousel
            message: Key message to convey visually
            cta: Call to action (for text space)
            brand_elements: Logo, colors, fonts
            sizes: List of size ratios needed

        Returns:
            Dict with images for each size
        """
        if not IMAGEN_AVAILABLE or not self.model:
            return {"error": "Imagen not available", "success": False}

        default_sizes = sizes or ["1:1", "16:9", "9:16", "4:5"]
        brand = brand_elements or {}

        base_prompt = f"""
Advertising creative for {product}
{f'Message: {message}' if message else ''}
{f'Leave clear space for CTA: {cta}' if cta else ''}

Style: Modern, attention-grabbing, professional advertising
{f'Brand colors: {brand.get("colors", [])}' if brand.get("colors") else ''}

High-impact visual that stops scrolling.
Clean composition with focal point.
Commercial quality suitable for paid advertising.
Leave text-safe zones for headlines and CTAs.
"""

        all_results = []

        for size in default_sizes:
            try:
                images = self.model.generate_images(
                    prompt=base_prompt.strip(),
                    number_of_images=2,
                    aspect_ratio=size,
                    safety_filter_level="block_some"
                )

                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

                for i, image in enumerate(images):
                    filename = f"ads/{size.replace(':', 'x')}/{timestamp}_{i}.png"

                    if self.bucket:
                        blob = self.bucket.blob(filename)
                        blob.upload_from_string(
                            image._image_bytes,
                            content_type='image/png'
                        )
                        blob.make_public()
                        url = blob.public_url
                    else:
                        url = f"data:image/png;base64,{base64.b64encode(image._image_bytes).decode()}"

                    all_results.append({
                        "url": url,
                        "filename": filename,
                        "aspect_ratio": size,
                        "ad_type": ad_type
                    })

            except Exception as e:
                all_results.append({
                    "aspect_ratio": size,
                    "error": str(e)
                })

        return {
            "success": True,
            "images": all_results,
            "prompt_used": base_prompt.strip(),
            "sizes_requested": default_sizes,
            "model": "imagen-4.0-generate-preview-05-20"
        }

    # ==================== BRAND ASSETS ====================

    async def generate_brand_visuals(
        self,
        brand_name: str,
        industry: str,
        style: str,
        colors: List[str] = None,
        visual_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate brand visual assets

        Args:
            brand_name: Company/brand name
            industry: Business industry
            style: modern, classic, playful, luxurious
            colors: Brand color palette
            visual_types: Types to generate

        Returns:
            Dict with various brand visuals
        """
        if not IMAGEN_AVAILABLE or not self.model:
            return {"error": "Imagen not available", "success": False}

        types = visual_types or ["hero_banner", "pattern", "icon_style"]
        color_text = f"Using colors: {', '.join(colors)}" if colors else ""

        results = {}

        prompts = {
            "hero_banner": f"""
Cinematic hero banner image for {brand_name}, a {industry} brand.
Style: {style}, premium, aspirational
{color_text}
Wide format banner suitable for website hero section.
Professional, high-impact, brand-appropriate imagery.
""",
            "pattern": f"""
Seamless brand pattern design for {brand_name} in {industry}.
Style: {style}, subtle, elegant
{color_text}
Tileable pattern suitable for backgrounds and packaging.
""",
            "icon_style": f"""
Set of modern icons representing {industry} for {brand_name}.
Style: {style}, consistent, clean
{color_text}
Minimalist icon design language.
""",
            "texture": f"""
Premium texture background for {brand_name} brand.
Style: {style}, sophisticated
{color_text}
Subtle texture for backgrounds and overlays.
"""
        }

        for visual_type in types:
            if visual_type in prompts:
                try:
                    images = self.model.generate_images(
                        prompt=prompts[visual_type].strip(),
                        number_of_images=2,
                        aspect_ratio="16:9" if visual_type == "hero_banner" else "1:1"
                    )

                    type_results = []
                    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

                    for i, image in enumerate(images):
                        filename = f"brand/{brand_name.lower().replace(' ', '_')}/{visual_type}_{timestamp}_{i}.png"

                        if self.bucket:
                            blob = self.bucket.blob(filename)
                            blob.upload_from_string(
                                image._image_bytes,
                                content_type='image/png'
                            )
                            blob.make_public()
                            url = blob.public_url
                        else:
                            url = f"data:image/png;base64,{base64.b64encode(image._image_bytes).decode()}"

                        type_results.append({
                            "url": url,
                            "filename": filename
                        })

                    results[visual_type] = {
                        "success": True,
                        "images": type_results,
                        "prompt": prompts[visual_type].strip()
                    }

                except Exception as e:
                    results[visual_type] = {
                        "success": False,
                        "error": str(e)
                    }

        return {
            "success": True,
            "brand_name": brand_name,
            "results": results,
            "model": "imagen-4.0-generate-preview-05-20"
        }

    # ==================== IMAGE EDITING ====================

    async def edit_image(
        self,
        image_path: str,
        edit_prompt: str,
        mask_prompt: str = None,
        edit_mode: str = "inpaint"
    ) -> Dict[str, Any]:
        """
        Edit existing image with AI

        Args:
            image_path: Path or URL to source image
            edit_prompt: What to change
            mask_prompt: Area to edit (for inpainting)
            edit_mode: inpaint, outpaint, style_transfer

        Returns:
            Dict with edited image
        """
        if not IMAGEN_AVAILABLE or not self.model:
            return {"error": "Imagen not available", "success": False}

        try:
            # Load source image
            source_image = Image.load_from_file(image_path)

            # Generate edited versions
            if edit_mode == "inpaint":
                edited = self.model.edit_image(
                    prompt=edit_prompt,
                    base_image=source_image,
                    number_of_images=4
                )
            else:
                edited = self.model.generate_images(
                    prompt=edit_prompt,
                    number_of_images=4
                )

            results = []
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

            for i, image in enumerate(edited):
                filename = f"edited/{timestamp}_{i}.png"

                if self.bucket:
                    blob = self.bucket.blob(filename)
                    blob.upload_from_string(
                        image._image_bytes,
                        content_type='image/png'
                    )
                    blob.make_public()
                    url = blob.public_url
                else:
                    url = f"data:image/png;base64,{base64.b64encode(image._image_bytes).decode()}"

                results.append({
                    "url": url,
                    "filename": filename
                })

            return {
                "success": True,
                "images": results,
                "edit_prompt": edit_prompt,
                "edit_mode": edit_mode,
                "model": "imagen-4.0-generate-preview-05-20"
            }

        except Exception as e:
            return {"error": str(e), "success": False}


# ==================== SINGLETON INSTANCE ====================

_imagen_instance = None

def get_imagen_generator() -> ImagenGenerator:
    """Get singleton instance of ImagenGenerator"""
    global _imagen_instance
    if _imagen_instance is None:
        _imagen_instance = ImagenGenerator()
    return _imagen_instance
