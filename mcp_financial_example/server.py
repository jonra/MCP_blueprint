#!/usr/bin/env python3
"""
Financial Intelligence MCP Server - No API Keys Required
Uses only free, open APIs for seamless training experience
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Financial Intelligence MCP - No Keys Required")

# API Configuration - All completely free, no authentication
COINGECKO_BASE = "https://api.coingecko.com/api/v3"
EXCHANGERATE_BASE = "https://api.exchangerate-api.com/v4/latest"
COINCAP_BASE = "https://api.coincap.io/v2"

class FinancialDataClient:
    """Centralized client for all financial data APIs - No authentication required"""

    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_crypto_price_coingecko(self, symbol: str) -> Dict:
        """Get crypto price from CoinGecko (most comprehensive free crypto API)"""
        url = f"{COINGECKO_BASE}/simple/price"
        params = {
            'ids': symbol.lower(),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get(symbol.lower(), {})
        except Exception as e:
            print(f"CoinGecko API error: {e}")
        return {}

    async def get_crypto_price_coincap(self, symbol: str) -> Dict:
        """Get crypto price from CoinCap (alternative crypto API)"""
        url = f"{COINCAP_BASE}/assets/{symbol.lower()}"

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    asset_data = data.get('data', {})
                    if asset_data:
                        return {
                            'price_usd': float(asset_data.get('priceUsd', 0)),
                            'change_24h_percent': float(asset_data.get('changePercent24Hr', 0)),
                            'market_cap': float(asset_data.get('marketCapUsd', 0)),
                            'volume_24h': float(asset_data.get('volumeUsd24Hr', 0))
                        }
        except Exception as e:
            print(f"CoinCap API error: {e}")
        return {}

    async def get_exchange_rates(self, base_currency: str = "USD") -> Dict:
        """Get currency exchange rates (free, no key required)"""
        url = f"{EXCHANGERATE_BASE}/{base_currency}"

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('rates', {})
        except Exception as e:
            print(f"Exchange Rate API error: {e}")
        return {}

# =============================================================================
# PHASE 1: Basic Price Lookup (Training Step 1)
# =============================================================================

@mcp.tool
async def get_bitcoin_price() -> Dict:
    """Get current Bitcoin price from CoinGecko.

    Training Goal: Learn basic async API integration with error handling
    """
    async with FinancialDataClient() as client:
        data = await client.get_crypto_price_coingecko('bitcoin')

        if data:
            return {
                "asset": "Bitcoin (BTC)",
                "price_usd": data.get('usd', 0),
                "change_24h_percent": round(data.get('usd_24h_change', 0), 2),
                "market_cap": data.get('usd_market_cap', 0),
                "volume_24h": data.get('usd_24h_vol', 0),
                "timestamp": datetime.now().isoformat(),
                "source": "CoinGecko API",
                "training_note": "Phase 1: Single API call with comprehensive data!"
            }

        return {
            "error": "Failed to fetch Bitcoin price",
            "training_note": "This demonstrates error handling - API might be down or rate limited"
        }

@mcp.tool
async def get_crypto_price(symbol: str) -> Dict:
    """Get price for any cryptocurrency using CoinGecko.

    Args:
        symbol: Crypto name (e.g., 'bitcoin', 'ethereum', 'cardano')

    Training Goal: Learn parameter handling and dynamic API calls
    """
    async with FinancialDataClient() as client:
        data = await client.get_crypto_price_coingecko(symbol)

        if data:
            return {
                "asset": f"{symbol.title()} ({symbol.upper()})",
                "price_usd": data.get('usd', 0),
                "change_24h_percent": round(data.get('usd_24h_change', 0), 2),
                "market_cap": data.get('usd_market_cap', 0),
                "volume_24h": data.get('usd_24h_vol', 0),
                "timestamp": datetime.now().isoformat(),
                "source": "CoinGecko API"
            }

        return {
            "error": f"Failed to fetch price for {symbol}",
            "suggestion": "Try: bitcoin, ethereum, cardano, solana, dogecoin, litecoin"
        }

# =============================================================================
# PHASE 2: Multi-Source Data Comparison (Training Step 2)
# =============================================================================

@mcp.tool
async def compare_crypto_sources(symbol: str) -> Dict:
    """Compare crypto price from multiple sources to show data consistency.

    Args:
        symbol: Crypto symbol (e.g., 'bitcoin', 'ethereum')

    Training Goal: Learn parallel API calls and data source comparison
    """
    async with FinancialDataClient() as client:
        # Fetch from both sources in parallel
        coingecko_task = client.get_crypto_price_coingecko(symbol)
        coincap_task = client.get_crypto_price_coincap(symbol)

        coingecko_data, coincap_data = await asyncio.gather(
            coingecko_task, coincap_task, return_exceptions=True
        )

        results = {
            "symbol": symbol.upper(),
            "comparison_timestamp": datetime.now().isoformat(),
            "sources": {}
        }

        # Process CoinGecko data
        if isinstance(coingecko_data, dict) and coingecko_data:
            results["sources"]["coingecko"] = {
                "price_usd": coingecko_data.get('usd', 0),
                "change_24h_percent": coingecko_data.get('usd_24h_change', 0),
                "status": "success"
            }
        else:
            results["sources"]["coingecko"] = {"status": "failed", "error": str(coingecko_data) if isinstance(coingecko_data, Exception) else "No data"}

        # Process CoinCap data
        if isinstance(coincap_data, dict) and coincap_data:
            results["sources"]["coincap"] = {
                "price_usd": coincap_data.get('price_usd', 0),
                "change_24h_percent": coincap_data.get('change_24h_percent', 0),
                "status": "success"
            }
        else:
            results["sources"]["coincap"] = {"status": "failed", "error": str(coincap_data) if isinstance(coincap_data, Exception) else "No data"}

        # Calculate price difference if both sources available
        coingecko_price = results["sources"].get("coingecko", {}).get("price_usd", 0)
        coincap_price = results["sources"].get("coincap", {}).get("price_usd", 0)

        if coingecko_price and coincap_price:
            price_diff = abs(coingecko_price - coincap_price)
            price_diff_percent = (price_diff / coingecko_price) * 100
            results["analysis"] = {
                "price_difference_usd": round(price_diff, 2),
                "price_difference_percent": round(price_diff_percent, 4),
                "sources_agree": price_diff_percent < 0.1  # Less than 0.1% difference
            }

        results["training_note"] = "Phase 2: Multi-source comparison shows data reliability!"
        return results

@mcp.tool
async def get_top_cryptocurrencies(limit: int = 10) -> Dict:
    """Get top cryptocurrencies by market cap.

    Args:
        limit: Number of cryptocurrencies to return (1-250)

    Training Goal: Learn to handle larger datasets and pagination
    """
    if limit > 250:
        limit = 250
    if limit < 1:
        limit = 10

    async with FinancialDataClient() as client:
        url = f"{COINGECKO_BASE}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': limit,
            'page': 1,
            'sparkline': 'false'
        }

        try:
            async with client.session.get(url, params=params) as response:
                if response.status == 200:
                    coins = await response.json()

                    results = []
                    for coin in coins:
                        results.append({
                            "rank": coin.get('market_cap_rank', 0),
                            "name": coin.get('name', ''),
                            "symbol": coin.get('symbol', '').upper(),
                            "price_usd": coin.get('current_price', 0),
                            "market_cap": coin.get('market_cap', 0),
                            "change_24h_percent": round(coin.get('price_change_percentage_24h', 0), 2),
                            "volume_24h": coin.get('total_volume', 0)
                        })

                    return {
                        "top_cryptocurrencies": results,
                        "total_returned": len(results),
                        "timestamp": datetime.now().isoformat(),
                        "training_note": f"Phase 2: Retrieved top {len(results)} cryptocurrencies by market cap!"
                    }
        except Exception as e:
            return {"error": f"Failed to fetch top cryptocurrencies: {str(e)}"}

        return {"error": "No data available"}

# =============================================================================
# PHASE 3: Currency Analysis (Training Step 3)
# =============================================================================

@mcp.tool
async def analyze_crypto_vs_fiat(crypto_symbol: str, fiat_currencies: List[str] = ["EUR", "GBP", "JPY"]) -> Dict:
    """Compare cryptocurrency value across multiple fiat currencies.

    Args:
        crypto_symbol: Cryptocurrency to analyze (e.g., 'bitcoin')
        fiat_currencies: List of fiat currency codes to compare against

    Training Goal: Learn cross-API data combination and financial analysis
    """
    async with FinancialDataClient() as client:
        # Get crypto price in USD and exchange rates in parallel
        crypto_task = client.get_crypto_price_coingecko(crypto_symbol)
        rates_task = client.get_exchange_rates("USD")

        crypto_data, exchange_rates = await asyncio.gather(
            crypto_task, rates_task, return_exceptions=True
        )

        if isinstance(crypto_data, Exception) or not crypto_data:
            return {"error": f"Failed to fetch {crypto_symbol} price"}

        if isinstance(exchange_rates, Exception) or not exchange_rates:
            return {"error": "Failed to fetch exchange rates"}

        usd_price = crypto_data.get('usd', 0)
        change_24h = crypto_data.get('usd_24h_change', 0)

        results = {
            "cryptocurrency": crypto_symbol.title(),
            "base_price_usd": usd_price,
            "change_24h_percent": round(change_24h, 2),
            "prices_in_fiat": {},
            "analysis_timestamp": datetime.now().isoformat()
        }

        # Calculate prices in different fiat currencies
        for currency in fiat_currencies:
            if currency in exchange_rates:
                rate = exchange_rates[currency]
                price_in_fiat = usd_price * rate
                results["prices_in_fiat"][currency] = {
                    "price": round(price_in_fiat, 2),
                    "exchange_rate": rate,
                    "formatted": f"{price_in_fiat:,.2f} {currency}"
                }

        # Add purchasing power analysis
        if "EUR" in results["prices_in_fiat"] and "GBP" in results["prices_in_fiat"]:
            eur_price = results["prices_in_fiat"]["EUR"]["price"]
            gbp_price = results["prices_in_fiat"]["GBP"]["price"]

            results["purchasing_power_analysis"] = {
                "cheapest_currency": "EUR" if eur_price < gbp_price else "GBP",
                "price_difference_percent": round(abs(eur_price - gbp_price) / min(eur_price, gbp_price) * 100, 2)
            }

        results["training_note"] = "Phase 3: Cross-currency analysis with purchasing power insights!"
        return results

# =============================================================================
# PHASE 4: Market Intelligence Dashboard (Training Step 4)
# =============================================================================

@mcp.tool
async def crypto_market_overview() -> Dict:
    """Get comprehensive cryptocurrency market overview and sentiment analysis.

    Training Goal: Learn to synthesize multiple data sources into actionable intelligence
    """
    async with FinancialDataClient() as client:
        # Get market data for major cryptocurrencies
        major_cryptos = ['bitcoin', 'ethereum', 'cardano', 'solana', 'dogecoin']

        # Fetch all crypto data in parallel
        crypto_tasks = [client.get_crypto_price_coingecko(crypto) for crypto in major_cryptos]
        crypto_results = await asyncio.gather(*crypto_tasks, return_exceptions=True)

        # Also get top 10 for market overview
        top_10_url = f"{COINGECKO_BASE}/coins/markets"
        top_10_params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 10,
            'page': 1
        }

        try:
            async with client.session.get(top_10_url, params=top_10_params) as response:
                top_10_data = await response.json() if response.status == 200 else []
        except:
            top_10_data = []

        # Analyze market sentiment
        positive_changes = 0
        negative_changes = 0
        total_market_cap = 0
        major_crypto_data = {}

        for i, crypto in enumerate(major_cryptos):
            result = crypto_results[i]
            if isinstance(result, dict) and result:
                change_24h = result.get('usd_24h_change', 0)
                if change_24h > 0:
                    positive_changes += 1
                elif change_24h < 0:
                    negative_changes += 1

                major_crypto_data[crypto] = {
                    "price_usd": result.get('usd', 0),
                    "change_24h_percent": round(change_24h, 2),
                    "market_cap": result.get('usd_market_cap', 0)
                }
                total_market_cap += result.get('usd_market_cap', 0)

        # Determine market sentiment
        if positive_changes > negative_changes:
            sentiment = "Bullish"
            sentiment_score = (positive_changes / len(major_cryptos)) * 100
        elif negative_changes > positive_changes:
            sentiment = "Bearish"
            sentiment_score = (negative_changes / len(major_cryptos)) * 100
        else:
            sentiment = "Mixed"
            sentiment_score = 50

        # Calculate total market cap from top 10
        total_top_10_cap = sum(coin.get('market_cap', 0) for coin in top_10_data if coin.get('market_cap'))

        return {
            "market_overview": {
                "timestamp": datetime.now().isoformat(),
                "overall_sentiment": sentiment,
                "sentiment_score": round(sentiment_score, 1),
                "major_cryptos_analyzed": len(major_crypto_data),
                "positive_performers": positive_changes,
                "negative_performers": negative_changes,
                "total_major_market_cap": total_market_cap
            },
            "major_cryptocurrencies": major_crypto_data,
            "top_10_summary": {
                "total_market_cap": total_top_10_cap,
                "bitcoin_dominance": round((major_crypto_data.get('bitcoin', {}).get('market_cap', 0) / total_top_10_cap * 100), 2) if total_top_10_cap > 0 else 0,
                "top_performer": max(top_10_data, key=lambda x: x.get('price_change_percentage_24h', -999999), default={}).get('name', 'N/A') if top_10_data else 'N/A'
            },
            "trading_signals": {
                "recommendation": "BUY" if sentiment == "Bullish" and sentiment_score > 70 else "HOLD" if sentiment == "Mixed" else "CAUTION",
                "confidence": "High" if sentiment_score > 80 or sentiment_score < 20 else "Medium",
                "key_insight": f"Market shows {sentiment.lower()} sentiment with {positive_changes}/{len(major_cryptos)} major cryptos performing positively"
            },
            "training_note": "Phase 4: Complete market intelligence with sentiment analysis and trading signals!"
        }

# =============================================================================
# Helper Tools for Training
# =============================================================================

@mcp.tool
def get_training_info() -> Dict:
    """Get comprehensive information about this training MCP server."""
    return {
        "server_name": "Financial Intelligence MCP - No API Keys Required",
        "purpose": "Learn MCP development through free financial APIs",
        "training_phases": {
            "phase_1": {
                "name": "Basic API Integration",
                "tools": ["get_bitcoin_price", "get_crypto_price"],
                "goal": "Learn async API calls and error handling"
            },
            "phase_2": {
                "name": "Multi-Source Data Comparison",
                "tools": ["compare_crypto_sources", "get_top_cryptocurrencies"],
                "goal": "Learn parallel API calls and data validation"
            },
            "phase_3": {
                "name": "Cross-Market Analysis",
                "tools": ["analyze_crypto_vs_fiat"],
                "goal": "Learn to combine different API types for insights"
            },
            "phase_4": {
                "name": "Market Intelligence",
                "tools": ["crypto_market_overview"],
                "goal": "Learn to synthesize data into actionable intelligence"
            }
        },
        "apis_used": [
            "CoinGecko API (comprehensive crypto data)",
            "CoinCap API (alternative crypto data)",
            "ExchangeRate-API (currency conversion)"
        ],
        "advantages": [
            "No API keys required - works immediately",
            "High rate limits suitable for training",
            "Real-time financial data for relevant examples",
            "Multiple data sources for reliability lessons"
        ],
        "sample_queries": [
            "What's Bitcoin's current price?",
            "Compare Bitcoin prices from different sources",
            "Show me the top 10 cryptocurrencies",
            "Analyze Bitcoin value in EUR and GBP",
            "Give me a complete crypto market overview"
        ],
        "next_steps": "Try each phase's tools in order to see complexity progression!"
    }

@mcp.tool
def get_supported_cryptocurrencies() -> Dict:
    """Get list of commonly supported cryptocurrencies for training examples."""
    return {
        "major_cryptocurrencies": [
            "bitcoin", "ethereum", "cardano", "solana", "dogecoin",
            "litecoin", "chainlink", "polkadot", "avalanche-2", "shiba-inu"
        ],
        "training_favorites": [
            "bitcoin - The original cryptocurrency",
            "ethereum - Smart contract platform",
            "dogecoin - Meme coin with high volatility",
            "cardano - Proof-of-stake blockchain",
            "solana - High-speed blockchain"
        ],
        "supported_fiat_currencies": [
            "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR"
        ],
        "usage_note": "Use the exact names from 'major_cryptocurrencies' list in the API calls"
    }

if __name__ == "__main__":
    mcp.run()
