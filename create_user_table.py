"""
Create User Table in BigQuery for Cloud Run Application
This script creates a user table to store user information for authentication and preferences
"""

from google.cloud import bigquery
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = 'cryptobot-462709'
DATASET_ID = 'crypto_trading_data'
TABLE_ID = 'users'


def create_user_table():
    """Create user table with comprehensive schema for Cloud Run authentication"""

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'

    # Define user table schema
    schema = [
        # User identification
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED", description="Unique user identifier (UUID)"),
        bigquery.SchemaField("email", "STRING", mode="REQUIRED", description="User email address"),
        bigquery.SchemaField("username", "STRING", mode="REQUIRED", description="User display name"),

        # Authentication
        bigquery.SchemaField("password_hash", "STRING", mode="REQUIRED", description="Hashed password (bcrypt)"),
        bigquery.SchemaField("email_verified", "BOOLEAN", mode="REQUIRED", description="Email verification status"),
        bigquery.SchemaField("verification_token", "STRING", description="Email verification token"),
        bigquery.SchemaField("reset_token", "STRING", description="Password reset token"),
        bigquery.SchemaField("reset_token_expires", "TIMESTAMP", description="Password reset token expiration"),

        # Account status
        bigquery.SchemaField("account_status", "STRING", mode="REQUIRED", description="active, suspended, deleted"),
        bigquery.SchemaField("subscription_tier", "STRING", mode="REQUIRED", description="free, basic, premium, enterprise"),
        bigquery.SchemaField("subscription_expires", "TIMESTAMP", description="Subscription expiration date"),

        # Profile information
        bigquery.SchemaField("first_name", "STRING", description="User first name"),
        bigquery.SchemaField("last_name", "STRING", description="User last name"),
        bigquery.SchemaField("profile_image_url", "STRING", description="URL to profile image"),
        bigquery.SchemaField("phone_number", "STRING", description="User phone number"),
        bigquery.SchemaField("country", "STRING", description="User country"),
        bigquery.SchemaField("timezone", "STRING", description="User timezone"),

        # Trading preferences
        bigquery.SchemaField("default_currency", "STRING", description="Default currency (USD, EUR, etc)"),
        bigquery.SchemaField("favorite_pairs", "STRING", mode="REPEATED", description="List of favorite trading pairs"),
        bigquery.SchemaField("watchlist", "STRING", mode="REPEATED", description="Watchlist of crypto pairs"),
        bigquery.SchemaField("alert_preferences", "JSON", description="JSON object with alert settings"),

        # UI preferences
        bigquery.SchemaField("theme", "STRING", description="UI theme: light, dark"),
        bigquery.SchemaField("default_chart_type", "STRING", description="Default chart type: candlestick, line, etc"),
        bigquery.SchemaField("default_timeframe", "STRING", description="Default timeframe: 1D, 1H, 5M"),
        bigquery.SchemaField("show_elliott_wave", "BOOLEAN", description="Show Elliott Wave indicators"),
        bigquery.SchemaField("show_fibonacci", "BOOLEAN", description="Show Fibonacci levels"),
        bigquery.SchemaField("ui_preferences", "JSON", description="JSON object with additional UI settings"),

        # Trading settings
        bigquery.SchemaField("risk_tolerance", "STRING", description="low, medium, high"),
        bigquery.SchemaField("auto_trading_enabled", "BOOLEAN", description="Auto-trading feature enabled"),
        bigquery.SchemaField("max_position_size", "FLOAT", description="Maximum position size in USD"),
        bigquery.SchemaField("stop_loss_percentage", "FLOAT", description="Default stop loss percentage"),
        bigquery.SchemaField("take_profit_percentage", "FLOAT", description="Default take profit percentage"),

        # API keys (encrypted)
        bigquery.SchemaField("kraken_api_key_encrypted", "STRING", description="Encrypted Kraken API key"),
        bigquery.SchemaField("kraken_api_secret_encrypted", "STRING", description="Encrypted Kraken API secret"),

        # Activity tracking
        bigquery.SchemaField("last_login", "TIMESTAMP", description="Last login timestamp"),
        bigquery.SchemaField("last_activity", "TIMESTAMP", description="Last activity timestamp"),
        bigquery.SchemaField("login_count", "INTEGER", description="Total number of logins"),
        bigquery.SchemaField("total_trades", "INTEGER", description="Total number of trades executed"),
        bigquery.SchemaField("total_pnl", "FLOAT", description="Total profit/loss in USD"),

        # Metadata
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED", description="Account creation timestamp"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED", description="Last update timestamp"),
        bigquery.SchemaField("created_by", "STRING", description="Created by (system, admin, user)"),
        bigquery.SchemaField("notes", "STRING", description="Admin notes"),

        # Session management
        bigquery.SchemaField("session_token", "STRING", description="Current session token"),
        bigquery.SchemaField("session_expires", "TIMESTAMP", description="Session expiration time"),
        bigquery.SchemaField("refresh_token", "STRING", description="Refresh token for session renewal"),

        # Feature flags
        bigquery.SchemaField("features_enabled", "JSON", description="JSON object with feature flags"),
        bigquery.SchemaField("beta_features", "BOOLEAN", description="Beta features access"),
    ]

    # Table configuration
    table = bigquery.Table(table_ref, schema=schema)
    table.description = "User accounts table for AI Algo Trade Hits application"

    # Add clustering for better query performance
    table.clustering_fields = ["email", "account_status", "subscription_tier"]

    try:
        # Check if table exists
        try:
            existing_table = client.get_table(table_ref)
            logger.info(f"Table {table_ref} already exists")

            # Update schema if needed
            existing_table.schema = schema
            updated_table = client.update_table(existing_table, ["schema"])
            logger.info(f"Updated schema for table {table_ref}")
            return True

        except Exception as e:
            # Table doesn't exist, create it
            logger.info(f"Creating new table {table_ref}")
            created_table = client.create_table(table)
            logger.info(f"Successfully created table {table_ref}")

            # Create indexes for common queries
            logger.info("Table created with clustering on: email, account_status, subscription_tier")
            return True

    except Exception as e:
        logger.error(f"Error creating/updating user table: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def create_trading_sessions_table():
    """Create trading sessions table to track user activity"""

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.trading_sessions'

    schema = [
        bigquery.SchemaField("session_id", "STRING", mode="REQUIRED", description="Unique session identifier"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED", description="User ID foreign key"),
        bigquery.SchemaField("start_time", "TIMESTAMP", mode="REQUIRED", description="Session start time"),
        bigquery.SchemaField("end_time", "TIMESTAMP", description="Session end time"),
        bigquery.SchemaField("ip_address", "STRING", description="User IP address"),
        bigquery.SchemaField("user_agent", "STRING", description="User agent string"),
        bigquery.SchemaField("device_type", "STRING", description="desktop, mobile, tablet"),
        bigquery.SchemaField("browser", "STRING", description="Browser name"),
        bigquery.SchemaField("location", "STRING", description="Geographic location"),
        bigquery.SchemaField("actions_count", "INTEGER", description="Number of actions in session"),
        bigquery.SchemaField("trades_count", "INTEGER", description="Number of trades in session"),
        bigquery.SchemaField("session_duration_seconds", "INTEGER", description="Total session duration"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED", description="Record creation time"),
    ]

    table = bigquery.Table(table_ref, schema=schema)
    table.description = "User trading sessions tracking table"
    table.clustering_fields = ["user_id", "start_time"]

    try:
        created_table = client.create_table(table)
        logger.info(f"Successfully created table {table_ref}")
        return True
    except Exception as e:
        if "Already Exists" in str(e):
            logger.info(f"Table {table_ref} already exists")
            return True
        logger.error(f"Error creating sessions table: {str(e)}")
        return False


def create_user_trades_table():
    """Create user trades table to store trading history"""

    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f'{PROJECT_ID}.{DATASET_ID}.user_trades'

    schema = [
        bigquery.SchemaField("trade_id", "STRING", mode="REQUIRED", description="Unique trade identifier"),
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED", description="User ID foreign key"),
        bigquery.SchemaField("pair", "STRING", mode="REQUIRED", description="Trading pair (e.g., BTCUSD)"),
        bigquery.SchemaField("trade_type", "STRING", mode="REQUIRED", description="buy, sell"),
        bigquery.SchemaField("order_type", "STRING", description="market, limit, stop-loss, take-profit"),
        bigquery.SchemaField("quantity", "FLOAT", mode="REQUIRED", description="Trade quantity"),
        bigquery.SchemaField("entry_price", "FLOAT", mode="REQUIRED", description="Entry price"),
        bigquery.SchemaField("exit_price", "FLOAT", description="Exit price"),
        bigquery.SchemaField("stop_loss", "FLOAT", description="Stop loss price"),
        bigquery.SchemaField("take_profit", "FLOAT", description="Take profit price"),
        bigquery.SchemaField("fees", "FLOAT", description="Trading fees"),
        bigquery.SchemaField("pnl", "FLOAT", description="Profit/Loss in USD"),
        bigquery.SchemaField("pnl_percentage", "FLOAT", description="Profit/Loss percentage"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED", description="open, closed, cancelled, pending"),
        bigquery.SchemaField("entry_datetime", "TIMESTAMP", mode="REQUIRED", description="Trade entry time"),
        bigquery.SchemaField("exit_datetime", "TIMESTAMP", description="Trade exit time"),
        bigquery.SchemaField("strategy_used", "STRING", description="Strategy name"),
        bigquery.SchemaField("elliott_wave_position", "INTEGER", description="Elliott wave position at entry"),
        bigquery.SchemaField("fib_level_entry", "FLOAT", description="Fibonacci level at entry"),
        bigquery.SchemaField("rsi_at_entry", "FLOAT", description="RSI at entry"),
        bigquery.SchemaField("macd_at_entry", "FLOAT", description="MACD at entry"),
        bigquery.SchemaField("notes", "STRING", description="Trade notes"),
        bigquery.SchemaField("automated", "BOOLEAN", description="Was this an automated trade"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED", description="Record creation time"),
    ]

    table = bigquery.Table(table_ref, schema=schema)
    table.description = "User trading history table"
    table.clustering_fields = ["user_id", "entry_datetime"]

    try:
        created_table = client.create_table(table)
        logger.info(f"Successfully created table {table_ref}")
        return True
    except Exception as e:
        if "Already Exists" in str(e):
            logger.info(f"Table {table_ref} already exists")
            return True
        logger.error(f"Error creating trades table: {str(e)}")
        return False


def main():
    """Main function to create all user-related tables"""

    logger.info("="*60)
    logger.info("Creating User Tables for Cloud Run Application")
    logger.info("="*60)

    success = True

    # Create main user table
    logger.info("Creating users table...")
    if not create_user_table():
        success = False
        logger.error("Failed to create users table")

    # Create trading sessions table
    logger.info("\nCreating trading_sessions table...")
    if not create_trading_sessions_table():
        success = False
        logger.error("Failed to create trading_sessions table")

    # Create user trades table
    logger.info("\nCreating user_trades table...")
    if not create_user_trades_table():
        success = False
        logger.error("Failed to create user_trades table")

    logger.info("="*60)
    if success:
        logger.info("All user tables created successfully!")
    else:
        logger.error("Some tables failed to create")
    logger.info("="*60)


if __name__ == "__main__":
    main()
