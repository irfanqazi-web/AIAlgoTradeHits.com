"""
Tool Registry and Trading Tools for AIAlgoTradeHits.com
Implements function calling for AI Agents
"""

import os
from typing import Dict, List, Any, Callable
from datetime import datetime


class ToolRegistry:
    """Registry for managing agent tools"""

    def __init__(self):
        self.tools: Dict[str, Dict] = {}
        self.handlers: Dict[str, Callable] = {}

    def register(self, name: str, definition: Dict, handler: Callable):
        """Register a new tool with its definition and handler"""
        self.tools[name] = definition
        self.handlers[name] = handler

    def get_definitions(self) -> List[Dict]:
        """Get all tool definitions for Claude API"""
        return list(self.tools.values())

    def execute(self, name: str, input_data: Dict) -> Any:
        """Execute a tool by name"""
        if name not in self.handlers:
            return {"error": f"Unknown tool: {name}"}
        try:
            return self.handlers[name](input_data)
        except Exception as e:
            return {"error": str(e)}


class TradingTools:
    """
    Trading-specific tools for the Trading Agent.
    Provides access to market data, indicators, and alerts.
    """

    def __init__(self):
        self._bigquery = None

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

    @staticmethod
    def get_tool_definitions() -> List[Dict]:
        """Return tool definitions for Claude API"""
        return [
            {
                "name": "get_market_data",
                "description": "Fetch real-time market data including OHLCV and technical indicators for a stock or crypto symbol",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker (e.g., AAPL, GOOGL) or crypto symbol (e.g., BTC, ETH)"
                        },
                        "interval": {
                            "type": "string",
                            "enum": ["1day", "1h", "5min"],
                            "description": "Data interval/timeframe"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "calculate_growth_score",
                "description": "Calculate the Growth Score (0-100) for a symbol based on RSI, MACD, ADX, and SMA_200",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock or crypto symbol"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "detect_rise_cycle",
                "description": "Check EMA 12/26 crossover status to detect rise or fall cycles",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock or crypto symbol"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "query_bigquery",
                "description": "Execute a SQL query on the trading data warehouse",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "SQL query to execute (use aialgotradehits.crypto_trading_data tables)"
                        }
                    },
                    "required": ["sql"]
                }
            },
            {
                "name": "send_alert",
                "description": "Send a trading alert notification",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock or crypto symbol"
                        },
                        "signal": {
                            "type": "string",
                            "enum": ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"],
                            "description": "Trading signal"
                        },
                        "message": {
                            "type": "string",
                            "description": "Alert message with details"
                        }
                    },
                    "required": ["symbol", "signal", "message"]
                }
            },
            {
                "name": "get_rise_cycle_candidates",
                "description": "Get stocks/cryptos that recently entered a rise cycle (EMA 12 crossed above EMA 26)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "asset_type": {
                            "type": "string",
                            "enum": ["stocks", "crypto", "all"],
                            "description": "Type of assets to screen"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_top_growth_scores",
                "description": "Get assets with the highest Growth Scores",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "min_score": {
                            "type": "integer",
                            "description": "Minimum Growth Score (0-100)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results"
                        }
                    },
                    "required": []
                }
            }
        ]

    def get_market_data(self, input_data: Dict) -> Dict:
        """Fetch market data from BigQuery"""
        symbol = input_data.get("symbol", "").upper()
        interval = input_data.get("interval", "1day")

        if not self.bigquery:
            return {"error": "BigQuery not available"}

        # Determine table based on interval
        table_map = {
            "1day": "stocks_daily_clean",
            "1h": "stocks_hourly_clean",
            "5min": "v2_stocks_5min"
        }
        table = table_map.get(interval, "stocks_daily_clean")

        query = f"""
        SELECT symbol, datetime, open, high, low, close, volume,
               rsi, macd, macd_histogram, adx, sma_20, sma_50, sma_200,
               ema_12, ema_26, bb_upper, bb_lower, atr
        FROM `aialgotradehits.crypto_trading_data.{table}`
        WHERE symbol = '{symbol}'
        ORDER BY datetime DESC
        LIMIT 1
        """

        try:
            result = list(self.bigquery.query(query).result())
            if result:
                row = result[0]
                return {
                    "symbol": row.symbol,
                    "datetime": str(row.datetime),
                    "open": float(row.open) if row.open else None,
                    "high": float(row.high) if row.high else None,
                    "low": float(row.low) if row.low else None,
                    "close": float(row.close) if row.close else None,
                    "volume": int(row.volume) if row.volume else None,
                    "rsi": float(row.rsi) if row.rsi else None,
                    "macd": float(row.macd) if row.macd else None,
                    "macd_histogram": float(row.macd_histogram) if row.macd_histogram else None,
                    "adx": float(row.adx) if row.adx else None,
                    "sma_20": float(row.sma_20) if row.sma_20 else None,
                    "sma_50": float(row.sma_50) if row.sma_50 else None,
                    "sma_200": float(row.sma_200) if row.sma_200 else None,
                    "ema_12": float(row.ema_12) if row.ema_12 else None,
                    "ema_26": float(row.ema_26) if row.ema_26 else None
                }
            return {"error": f"No data found for {symbol}"}
        except Exception as e:
            return {"error": str(e)}

    def calculate_growth_score(self, input_data: Dict) -> Dict:
        """Calculate Growth Score for a symbol"""
        symbol = input_data.get("symbol", "").upper()

        # Get market data first
        market_data = self.get_market_data({"symbol": symbol, "interval": "1day"})

        if "error" in market_data:
            return market_data

        score = 0
        components = []

        # RSI between 50-70: +25 points
        rsi = market_data.get("rsi")
        if rsi and 50 <= rsi <= 70:
            score += 25
            components.append(f"RSI {rsi:.1f} in sweet spot (+25)")
        elif rsi:
            components.append(f"RSI {rsi:.1f} outside sweet spot (+0)")

        # MACD histogram > 0: +25 points
        macd_hist = market_data.get("macd_histogram")
        if macd_hist and macd_hist > 0:
            score += 25
            components.append(f"MACD histogram {macd_hist:.4f} positive (+25)")
        elif macd_hist:
            components.append(f"MACD histogram {macd_hist:.4f} negative (+0)")

        # ADX > 25: +25 points
        adx = market_data.get("adx")
        if adx and adx > 25:
            score += 25
            components.append(f"ADX {adx:.1f} strong trend (+25)")
        elif adx:
            components.append(f"ADX {adx:.1f} weak trend (+0)")

        # Close > SMA_200: +25 points
        close = market_data.get("close")
        sma_200 = market_data.get("sma_200")
        if close and sma_200 and close > sma_200:
            score += 25
            components.append(f"Close {close:.2f} > SMA_200 {sma_200:.2f} (+25)")
        elif close and sma_200:
            components.append(f"Close {close:.2f} < SMA_200 {sma_200:.2f} (+0)")

        # Determine recommendation
        if score >= 75:
            recommendation = "STRONG_BUY"
        elif score >= 50:
            recommendation = "BUY"
        elif score >= 25:
            recommendation = "HOLD"
        else:
            recommendation = "AVOID"

        return {
            "symbol": symbol,
            "growth_score": score,
            "recommendation": recommendation,
            "components": components,
            "calculated_at": datetime.now().isoformat()
        }

    def detect_rise_cycle(self, input_data: Dict) -> Dict:
        """Detect EMA rise/fall cycle status"""
        symbol = input_data.get("symbol", "").upper()

        if not self.bigquery:
            return {"error": "BigQuery not available"}

        query = f"""
        WITH latest AS (
            SELECT symbol, datetime, ema_12, ema_26,
                   LAG(ema_12) OVER (ORDER BY datetime) as prev_ema_12,
                   LAG(ema_26) OVER (ORDER BY datetime) as prev_ema_26
            FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
            WHERE symbol = '{symbol}'
            ORDER BY datetime DESC
            LIMIT 2
        )
        SELECT * FROM latest ORDER BY datetime DESC LIMIT 1
        """

        try:
            result = list(self.bigquery.query(query).result())
            if result:
                row = result[0]
                ema_12 = float(row.ema_12) if row.ema_12 else 0
                ema_26 = float(row.ema_26) if row.ema_26 else 0
                prev_ema_12 = float(row.prev_ema_12) if row.prev_ema_12 else 0
                prev_ema_26 = float(row.prev_ema_26) if row.prev_ema_26 else 0

                in_rise_cycle = ema_12 > ema_26
                rise_cycle_start = in_rise_cycle and prev_ema_12 <= prev_ema_26
                fall_cycle_start = not in_rise_cycle and prev_ema_12 >= prev_ema_26

                return {
                    "symbol": symbol,
                    "in_rise_cycle": in_rise_cycle,
                    "rise_cycle_start": rise_cycle_start,
                    "fall_cycle_start": fall_cycle_start,
                    "ema_12": ema_12,
                    "ema_26": ema_26,
                    "status": "RISE_CYCLE" if in_rise_cycle else "FALL_CYCLE",
                    "signal": "BUY" if rise_cycle_start else ("SELL" if fall_cycle_start else "HOLD")
                }
            return {"error": f"No data found for {symbol}"}
        except Exception as e:
            return {"error": str(e)}

    def query_bigquery(self, input_data: Dict) -> Dict:
        """Execute a SQL query on BigQuery"""
        sql = input_data.get("sql", "")

        if not self.bigquery:
            return {"error": "BigQuery not available"}

        # Basic security check
        sql_lower = sql.lower()
        if any(keyword in sql_lower for keyword in ["drop", "delete", "update", "insert", "truncate"]):
            return {"error": "Only SELECT queries are allowed"}

        try:
            result = list(self.bigquery.query(sql).result())
            # Convert to list of dicts
            rows = []
            for row in result[:100]:  # Limit to 100 rows
                rows.append(dict(row))
            return {
                "row_count": len(rows),
                "data": rows
            }
        except Exception as e:
            return {"error": str(e)}

    def send_alert(self, input_data: Dict) -> Dict:
        """Send a trading alert"""
        symbol = input_data.get("symbol", "")
        signal = input_data.get("signal", "")
        message = input_data.get("message", "")

        # In production, this would integrate with:
        # - Email (SendGrid)
        # - SMS (Twilio)
        # - Push notifications
        # - Slack/Discord webhooks

        alert = {
            "symbol": symbol,
            "signal": signal,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "status": "queued"
        }

        print(f"[ALERT] {signal} on {symbol}: {message}")

        return {
            "status": "sent",
            "alert": alert
        }

    def get_rise_cycle_candidates(self, input_data: Dict) -> Dict:
        """Get assets that recently entered a rise cycle"""
        asset_type = input_data.get("asset_type", "all")
        limit = input_data.get("limit", 20)

        if not self.bigquery:
            return {"error": "BigQuery not available"}

        tables = []
        if asset_type in ["stocks", "all"]:
            tables.append("stocks_daily_clean")
        if asset_type in ["crypto", "all"]:
            tables.append("crypto_daily_clean")

        results = []
        for table in tables:
            query = f"""
            WITH cycles AS (
                SELECT symbol, datetime, close, ema_12, ema_26, rsi, volume,
                       LAG(ema_12) OVER (PARTITION BY symbol ORDER BY datetime) as prev_ema_12,
                       LAG(ema_26) OVER (PARTITION BY symbol ORDER BY datetime) as prev_ema_26
                FROM `aialgotradehits.crypto_trading_data.{table}`
                WHERE datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
            )
            SELECT * FROM cycles
            WHERE ema_12 > ema_26
              AND prev_ema_12 <= prev_ema_26
            ORDER BY datetime DESC
            LIMIT {limit}
            """

            try:
                rows = list(self.bigquery.query(query).result())
                for row in rows:
                    results.append({
                        "symbol": row.symbol,
                        "datetime": str(row.datetime),
                        "close": float(row.close) if row.close else None,
                        "rsi": float(row.rsi) if row.rsi else None,
                        "source": table
                    })
            except Exception as e:
                print(f"Error querying {table}: {e}")

        return {
            "candidates": results,
            "count": len(results)
        }

    def get_top_growth_scores(self, input_data: Dict) -> Dict:
        """Get assets with highest Growth Scores"""
        min_score = input_data.get("min_score", 75)
        limit = input_data.get("limit", 20)

        if not self.bigquery:
            return {"error": "BigQuery not available"}

        query = f"""
        SELECT symbol, datetime, close, growth_score, trend_regime, in_rise_cycle, recommendation
        FROM `aialgotradehits.crypto_trading_data.stocks_daily_clean`
        WHERE growth_score >= {min_score}
          AND datetime >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 DAY)
        ORDER BY growth_score DESC, datetime DESC
        LIMIT {limit}
        """

        try:
            result = list(self.bigquery.query(query).result())
            rows = []
            for row in result:
                rows.append({
                    "symbol": row.symbol,
                    "datetime": str(row.datetime),
                    "close": float(row.close) if row.close else None,
                    "growth_score": int(row.growth_score) if row.growth_score else 0,
                    "trend_regime": row.trend_regime,
                    "in_rise_cycle": row.in_rise_cycle,
                    "recommendation": row.recommendation
                })
            return {
                "top_scores": rows,
                "count": len(rows)
            }
        except Exception as e:
            return {"error": str(e)}
