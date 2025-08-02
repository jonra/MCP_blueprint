#!/usr/bin/env python3
"""
Streamlined Financial MCP Server - Data Collection & Aggregation Demo
Strategy: MCP handles data collection, LLM handles intelligence & synthesis

This server demonstrates clean separation of concerns:
- MCP Tools: Fetch and structure data from multiple sources
- LLM (Claude): Synthesize data into insights and recommendations
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Financial Data Aggregation MCP")

# API Configuration - All free, no authentication required
COINGECKO_BASE = "https://api.coingecko.com/api/v3"
EXCHANGERATE_BASE = "https://api.exchangerate-api.com/v4/latest"
CRYPTOPANIC_BASE = "https://cryptopanic.com/api/v1"
REDDIT_CRYPTO_BASE = "https://www.reddit.com/r"

class FinancialDataClient:
    """Centralized client for financial data APIs"""

    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_crypto_data(self, symbols: List[str]) -> Dict:
        """Fetch cryptocurrency data from CoinGecko"""
        # Convert symbols to CoinGecko IDs (simplified mapping)
        symbol_map = {
            'bitcoin': 'bitcoin', 'btc': 'bitcoin',
            'ethereum': 'ethereum', 'eth': 'ethereum',
            'cardano': 'cardano', 'ada': 'cardano',
            'solana': 'solana', 'sol': 'solana',
            'dogecoin': 'dogecoin', 'doge': 'dogecoin'
        }

        mapped_symbols = [symbol_map.get(s.lower(), s.lower()) for s in symbols]
        ids_string = ','.join(mapped_symbols)

        url = f"{COINGECKO_BASE}/simple/price"
        params = {
            'ids': ids_string,
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_last_updated_at': 'true'
        }

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"CoinGecko API error: {e}")
        return {}

    async def fetch_news_data(self, sources: List[str]) -> Dict:
        """Fetch news from multiple sources"""
        news_data = {
            'cryptopanic': [],
            'reddit': [],
            'timestamp': datetime.now().isoformat()
        }

        if 'cryptopanic' in sources or 'all' in sources:
            try:
                url = f"{CRYPTOPANIC_BASE}/posts/"
                params = {
                    'auth_token': 'free',
                    'currencies': 'BTC,ETH',
                    'filter': 'hot',
                    'public': 'true'
                }
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        news_data['cryptopanic'] = data.get('results', [])[:5]
            except Exception as e:
                print(f"CryptoPanic error: {e}")

        if 'reddit' in sources or 'all' in sources:
            try:
                url = f"{REDDIT_CRYPTO_BASE}/cryptocurrency/hot.json"
                params = {'limit': 5}
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = data.get('data', {}).get('children', [])
                        news_data['reddit'] = [
                            {
                                'title': post['data'].get('title', ''),
                                'score': post['data'].get('score', 0),
                                'num_comments': post['data'].get('num_comments', 0),
                                'created_utc': post['data'].get('created_utc', 0),
                                'upvote_ratio': post['data'].get('upvote_ratio', 0)
                            }
                            for post in posts[:5]
                        ]
            except Exception as e:
                print(f"Reddit error: {e}")

        return news_data

    async def fetch_exchange_rates(self, base: str) -> Dict:
        """Fetch currency exchange rates"""
        url = f"{EXCHANGERATE_BASE}/{base}"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"Exchange rate error: {e}")
        return {}

# =============================================================================
# MCP TOOLS - Data Collection & Aggregation Only
# =============================================================================

@mcp.tool
async def get_market_data(symbols: List[str]) -> Dict:
    """Fetch clean market data for specified cryptocurrencies.

    Returns structured price, volume, and market cap data without analysis.
    LLM uses this for: trend analysis, volatility assessment, comparisons.

    Args:
        symbols: List of crypto symbols (e.g., ['bitcoin', 'ethereum', 'cardano'])
    """
    async with FinancialDataClient() as client:
        raw_data = await client.fetch_crypto_data(symbols)

        if not raw_data:
            return {
                "error": "Failed to fetch market data",
                "requested_symbols": symbols,
                "timestamp": datetime.now().isoformat()
            }

        # Structure the data cleanly for LLM consumption
        market_data = {}
        for symbol_id, data in raw_data.items():
            market_data[symbol_id] = {
                "price_usd": data.get('usd', 0),
                "change_24h_percent": round(data.get('usd_24h_change', 0), 2),
                "market_cap": data.get('usd_market_cap', 0),
                "volume_24h": data.get('usd_24h_vol', 0),
                "last_updated": data.get('last_updated_at', 0)
            }

        return {
            "market_data": market_data,
            "data_source": "CoinGecko API",
            "timestamp": datetime.now().isoformat(),
            "symbols_found": len(market_data),
            "symbols_requested": len(symbols)
        }

@mcp.tool
async def get_news_feed(sources: List[str] = ["all"]) -> Dict:
    """Fetch structured news data from multiple sources.

    Returns raw news headlines and metadata without sentiment analysis.
    LLM uses this for: context building, event correlation, sentiment synthesis.

    Args:
        sources: News sources to fetch from (['cryptopanic', 'reddit', 'all'])
    """
    async with FinancialDataClient() as client:
        news_data = await client.fetch_news_data(sources)

        # Structure news data for easy LLM processing
        structured_news = {
            "news_sources": {},
            "total_items": 0,
            "fetch_timestamp": news_data.get('timestamp'),
            "sources_requested": sources
        }

        # Process CryptoPanic news
        if news_data.get('cryptopanic'):
            cryptopanic_items = []
            for item in news_data['cryptopanic']:
                cryptopanic_items.append({
                    "title": item.get('title', ''),
                    "published_at": item.get('published_at', ''),
                    "source": item.get('source', {}).get('title', 'Unknown'),
                    "currencies": item.get('currencies', []),
                    "kind": item.get('kind', 'news')
                })
            structured_news["news_sources"]["cryptopanic"] = {
                "items": cryptopanic_items,
                "count": len(cryptopanic_items)
            }
            structured_news["total_items"] += len(cryptopanic_items)

        # Process Reddit data
        if news_data.get('reddit'):
            reddit_items = []
            for item in news_data['reddit']:
                reddit_items.append({
                    "title": item.get('title', ''),
                    "engagement_score": item.get('score', 0),
                    "comment_count": item.get('num_comments', 0),
                    "upvote_ratio": item.get('upvote_ratio', 0),
                    "created_utc": item.get('created_utc', 0)
                })
            structured_news["news_sources"]["reddit"] = {
                "items": reddit_items,
                "count": len(reddit_items),
                "avg_engagement": sum(item['engagement_score'] for item in reddit_items) / len(reddit_items) if reddit_items else 0
            }
            structured_news["total_items"] += len(reddit_items)

        return structured_news

@mcp.tool
def get_risk_profile() -> Dict:
    """Get structured risk assessment profile and investment guidelines.

    Returns risk profile as structured data without applying it.
    LLM uses this for: applying consistent risk logic, explaining investment reasoning.
    """
    return {
        "risk_profile": [
            "Conservative investors should limit crypto allocation to 5-10% of total portfolio, focusing on Bitcoin and Ethereum with 6+ month holding periods.",
            "Moderate risk tolerance allows 10-20% crypto allocation across 3-4 major cryptocurrencies, accepting 20-30% volatility swings as normal market behavior.",
            "Aggressive investors can allocate 20-40% to crypto including smaller-cap altcoins, but must prepare for 50%+ drawdowns and multi-year recovery periods.",
            "Never invest more than you can afford to lose completely - cryptocurrency markets can experience 80-90% crashes during bear market cycles.",
            "Dollar-cost averaging over 6-12 months reduces timing risk, while taking profits at 2x-3x gains helps lock in returns during bull markets."
        ],
        "volatility_expectations": {
            "bitcoin": "Daily: ±5%, Monthly: ±25%, Annual: ±75%",
            "ethereum": "Daily: ±7%, Monthly: ±35%, Annual: ±85%",
            "altcoins": "Daily: ±10%, Monthly: ±50%, Annual: ±90%"
        },
        "key_principles": {
            "diversification": "Spread risk across multiple assets and time periods",
            "position_sizing": "Size positions based on conviction and risk tolerance",
            "time_horizon": "Minimum 12-18 months for any crypto investment",
            "emotional_discipline": "Avoid FOMO buying and panic selling during extreme moves"
        },
        "profile_version": "1.0",
        "last_updated": "2025-08-01"
    }

@mcp.tool
async def get_currency_rates(base: str = "USD") -> Dict:
    """Fetch current currency exchange rates.

    Returns clean exchange rate data without calculations.
    LLM uses this for: multi-currency analysis, purchasing power comparison.

    Args:
        base: Base currency for rates (default: USD)
    """
    async with FinancialDataClient() as client:
        rate_data = await client.fetch_exchange_rates(base)

        if not rate_data:
            return {
                "error": "Failed to fetch exchange rates",
                "base_currency": base,
                "timestamp": datetime.now().isoformat()
            }

        # Focus on major currencies for clean data
        major_currencies = ['EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY']
        major_rates = {}

        rates = rate_data.get('rates', {})
        for currency in major_currencies:
            if currency in rates:
                major_rates[currency] = rates[currency]

        return {
            "base_currency": base,
            "rates": major_rates,
            "all_rates_count": len(rates),
            "major_rates_count": len(major_rates),
            "last_updated": rate_data.get('date', ''),
            "timestamp": datetime.now().isoformat(),
            "data_source": "ExchangeRate-API"
        }

# =============================================================================
# Helper Tools
# =============================================================================

@mcp.tool
def get_server_info() -> Dict:
    """Get information about this MCP server and its capabilities."""
    return {
        "server_name": "Financial Data Aggregation MCP",
        "strategy": "Data Collection & Aggregation (LLM handles intelligence)",
        "tools": [
            {
                "name": "get_market_data",
                "purpose": "Clean price/volume data aggregation",
                "llm_uses": "Trend analysis, comparison, risk assessment"
            },
            {
                "name": "get_news_feed",
                "purpose": "Structured news aggregation",
                "llm_uses": "Context building, sentiment synthesis, event correlation"
            },
            {
                "name": "get_trading_rules",
                "purpose": "Business rules as structured data",
                "llm_uses": "Apply consistent decision framework"
            },
            {
                "name": "get_currency_rates",
                "purpose": "Currency exchange data",
                "llm_uses": "Multi-currency analysis, purchasing power comparison"
            }
        ],
        "demo_scenarios": [
            "Should I invest in Bitcoin or Ethereum?",
            "What's happening in crypto markets today?",
            "Compare Bitcoin price in different currencies",
            "Analyze recent crypto news sentiment"
        ],
        "data_sources": [
            "CoinGecko API (market data)",
            "CryptoPanic API (news)",
            "Reddit API (social sentiment)",
            "ExchangeRate-API (currency rates)"
        ],
        "key_principle": "MCP provides clean data, Claude provides intelligence"
    }

@mcp.tool
def get_supported_assets() -> Dict:
    """Get list of supported cryptocurrencies and currencies."""
    return {
        "cryptocurrencies": {
            "major": ["bitcoin", "ethereum", "cardano", "solana", "dogecoin"],
            "aliases": {
                "btc": "bitcoin",
                "eth": "ethereum",
                "ada": "cardano",
                "sol": "solana",
                "doge": "dogecoin"
            }
        },
        "fiat_currencies": {
            "supported": ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY"],
            "base_options": ["USD", "EUR", "GBP"]
        },
        "news_sources": {
            "available": ["cryptopanic", "reddit", "all"],
            "descriptions": {
                "cryptopanic": "Crypto-focused news aggregator",
                "reddit": "Social sentiment from r/cryptocurrency",
                "all": "Combined data from all sources"
            }
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Financial Data Aggregation MCP Server")
    print("📊 Strategy: Data Collection & Aggregation")
    print("🤖 LLM Role: Intelligence & Synthesis")
    print("🔧 All APIs are free - no authentication required")
    print("\n💡 Demo Flow:")
    print("   1. User asks investment question")
    print("   2. Claude calls multiple MCP tools for data")
    print("   3. Claude synthesizes data into intelligent response")
    mcp.run()
