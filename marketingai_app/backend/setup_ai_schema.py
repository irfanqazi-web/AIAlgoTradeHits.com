"""
Setup Enhanced BigQuery Schema for MarketingAI with AI Campaigns
Adds tables for AI-generated content, campaigns, and generated assets
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import bigquery

PROJECT_ID = 'aialgotradehits'
DATASET_ID = 'marketingai_data'


def setup_ai_schema():
    client = bigquery.Client(project=PROJECT_ID)
    dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"

    print("="*60)
    print("MarketingAI - AI Schema Enhancement")
    print("="*60)

    # Campaigns table
    campaigns_schema = [
        bigquery.SchemaField("campaign_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("brand_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("goals", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("platforms", "STRING", mode="REPEATED"),
        bigquery.SchemaField("duration_days", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("posts_per_day", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("strategy_json", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("content_calendar_json", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),  # draft, active, completed, paused
        bigquery.SchemaField("start_date", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("end_date", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("total_posts", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("posts_published", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("total_engagement", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE"),
    ]

    campaigns_table = bigquery.Table(f"{dataset_ref}.campaigns", schema=campaigns_schema)
    try:
        client.create_table(campaigns_table, exists_ok=True)
        print("Campaigns table created/verified")
    except Exception as e:
        print(f"Campaigns table error: {e}")

    # AI Generated Images table
    ai_images_schema = [
        bigquery.SchemaField("image_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("brand_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("campaign_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("content_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("prompt", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("enhanced_prompt", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("model", "STRING", mode="REQUIRED"),  # imagen-3.0, etc
        bigquery.SchemaField("style", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("aspect_ratio", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("gcs_url", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("cdn_url", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("generation_time_ms", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("is_favorite", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("used_count", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    ai_images_table = bigquery.Table(f"{dataset_ref}.ai_generated_images", schema=ai_images_schema)
    try:
        client.create_table(ai_images_table, exists_ok=True)
        print("AI Generated Images table created/verified")
    except Exception as e:
        print(f"AI Images table error: {e}")

    # AI Generated Videos table
    ai_videos_schema = [
        bigquery.SchemaField("video_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("brand_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("campaign_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("content_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("prompt", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("source_image_id", "STRING", mode="NULLABLE"),  # for image-to-video
        bigquery.SchemaField("model", "STRING", mode="REQUIRED"),  # veo-001, etc
        bigquery.SchemaField("style", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("duration_seconds", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("aspect_ratio", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("gcs_url", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("cdn_url", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("thumbnail_url", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("generation_time_ms", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),  # pending, processing, completed, failed
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    ai_videos_table = bigquery.Table(f"{dataset_ref}.ai_generated_videos", schema=ai_videos_schema)
    try:
        client.create_table(ai_videos_table, exists_ok=True)
        print("AI Generated Videos table created/verified")
    except Exception as e:
        print(f"AI Videos table error: {e}")

    # AI Generated Copy table
    ai_copy_schema = [
        bigquery.SchemaField("copy_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("brand_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("campaign_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("content_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("type", "STRING", mode="REQUIRED"),  # headline, caption, carousel, cta
        bigquery.SchemaField("platform", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("input_prompt", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("tone", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("target_audience", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("generated_headline", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("generated_caption", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("generated_hashtags", "STRING", mode="REPEATED"),
        bigquery.SchemaField("generated_cta", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("carousel_slides_json", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("model", "STRING", mode="REQUIRED"),  # gemini-2.0-flash, etc
        bigquery.SchemaField("is_favorite", "BOOLEAN", mode="NULLABLE"),
        bigquery.SchemaField("used_count", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    ai_copy_table = bigquery.Table(f"{dataset_ref}.ai_generated_copy", schema=ai_copy_schema)
    try:
        client.create_table(ai_copy_table, exists_ok=True)
        print("AI Generated Copy table created/verified")
    except Exception as e:
        print(f"AI Copy table error: {e}")

    # Campaign Analytics table
    campaign_analytics_schema = [
        bigquery.SchemaField("analytics_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("campaign_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("content_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("platform", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("impressions", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("reach", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("likes", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("comments", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("shares", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("saves", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("clicks", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("engagement_rate", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("followers_gained", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("video_views", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("avg_watch_time_sec", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("recorded_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    campaign_analytics_table = bigquery.Table(f"{dataset_ref}.campaign_analytics", schema=campaign_analytics_schema)
    campaign_analytics_table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="date"
    )
    try:
        client.create_table(campaign_analytics_table, exists_ok=True)
        print("Campaign Analytics table created/verified")
    except Exception as e:
        print(f"Campaign Analytics table error: {e}")

    # AI Agent Tasks table
    agent_tasks_schema = [
        bigquery.SchemaField("task_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("campaign_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("task_type", "STRING", mode="REQUIRED"),  # generate_content, analyze, optimize, respond
        bigquery.SchemaField("input_json", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("output_json", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),  # pending, running, completed, failed
        bigquery.SchemaField("error_message", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("execution_time_ms", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("tokens_used", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("cost_usd", "FLOAT64", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("completed_at", "TIMESTAMP", mode="NULLABLE"),
    ]

    agent_tasks_table = bigquery.Table(f"{dataset_ref}.agent_tasks", schema=agent_tasks_schema)
    try:
        client.create_table(agent_tasks_table, exists_ok=True)
        print("Agent Tasks table created/verified")
    except Exception as e:
        print(f"Agent Tasks table error: {e}")

    # Scheduled Posts table
    scheduled_posts_schema = [
        bigquery.SchemaField("schedule_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("content_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("campaign_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("platform", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("scheduled_time", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("timezone", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),  # scheduled, published, failed, cancelled
        bigquery.SchemaField("published_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("platform_post_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("error_message", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("retry_count", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    ]

    scheduled_posts_table = bigquery.Table(f"{dataset_ref}.scheduled_posts", schema=scheduled_posts_schema)
    try:
        client.create_table(scheduled_posts_table, exists_ok=True)
        print("Scheduled Posts table created/verified")
    except Exception as e:
        print(f"Scheduled Posts table error: {e}")

    print("\n" + "="*60)
    print("AI Schema Enhancement Complete!")
    print("="*60)
    print("""
New tables created:
  - campaigns: AI-powered marketing campaigns
  - ai_generated_images: Imagen-generated images
  - ai_generated_videos: Veo-generated videos
  - ai_generated_copy: Gemini-generated copy
  - campaign_analytics: Performance metrics
  - agent_tasks: AI agent task history
  - scheduled_posts: Content scheduling

AI Capabilities:
  - Gemini 2.5: Content generation, strategy, analytics
  - Imagen 3.0: Image generation
  - Veo 3.1: Video generation
  - Campaign Agent: Automated campaign management
""")


if __name__ == '__main__':
    setup_ai_schema()
