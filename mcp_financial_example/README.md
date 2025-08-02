# Financial Data Aggregation MCP Server

## 🎯 **Purpose**

This MCP server demonstrates the **ideal separation of concerns** between MCP tools and LLMs:

- **MCP Tools**: Handle data collection and aggregation from multiple APIs
- **LLM (Claude)**: Provides intelligence, synthesis, and recommendations

## 🏗️ **Architecture Strategy**

```
User Question → Claude → MCP Tools (Data) → Claude (Intelligence) → User Answer
```

**Key Principle**: MCP provides clean, structured data. Claude provides the intelligence.

## 🛠️ **Available Tools**

### 1. `get_market_data(symbols: List[str])`
**Purpose**: Fetch clean market data for cryptocurrencies  
**Returns**: Price, volume, market cap, 24h changes  
**LLM Uses**: Trend analysis, volatility assessment, comparisons

```python
# Example call
get_market_data(["bitcoin", "ethereum", "cardano"])
```

### 2. `get_news_feed(sources: List[str] = ["all"])`
**Purpose**: Aggregate news from multiple sources  
**Returns**: Headlines, timestamps, engagement metrics  
**LLM Uses**: Context building, sentiment synthesis, event correlation

```python
# Example calls
get_news_feed(["cryptopanic", "reddit"])
get_news_feed(["all"])  # Gets from all sources
```

### 3. `get_risk_profile()`
**Purpose**: Provide structured risk assessment guidelines and investment principles  
**Returns**: Risk tolerance guidelines, volatility expectations, investment strategies  
**LLM Uses**: Apply personalized risk logic, tailor investment advice to user profile

### 4. `get_currency_rates(base: str = "USD")`
**Purpose**: Fetch current exchange rates  
**Returns**: Major currency conversion rates  
**LLM Uses**: Multi-currency analysis, purchasing power comparison

## 🚀 **Quick Start**

### Prerequisites
- Python 3.8+
- Docker (optional, for development)

### Installation
```bash
# Install dependencies
pip install fastmcp aiohttp

# Run the server
python financial_mcp_server.py
```

### Test the Server
```bash
# Use MCP Inspector (if available)
mcp-inspector --transport stdio -- python financial_mcp_server.py

# Or test with curl (if using HTTP transport)
curl http://localhost:8000/tools
```

## 🎮 **Demo Scenarios**

### Scenario 1: Investment Decision
**User**: *"Should I invest $1000 in Bitcoin right now?"*

**Claude's Orchestration**:
1. `get_market_data(["bitcoin"])` → Current price and volatility
2. `get_news_feed(["all"])` → Recent Bitcoin news context
3. `get_trading_rules()` → Decision framework and thresholds
4. **Claude synthesizes**: *"Based on current 15% volatility, recent regulatory news, and our risk thresholds, I recommend..."*

### Scenario 2: Asset Comparison
**User**: *"Compare Bitcoin and Ethereum for investment"*

**Claude's Orchestration**:
1. `get_market_data(["bitcoin", "ethereum"])` → Side-by-side metrics
2. `get_news_feed(["all"])` → Recent news for both assets
3. `get_risk_profile()` → Risk assessment guidelines
4. **Claude synthesizes**: *"Bitcoin shows lower volatility (X%) vs Ethereum (Y%), and based on conservative risk guidelines..."*

### Scenario 3: Global Market View
**User**: *"What's happening in crypto markets today?"*

**Claude's Orchestration**:
1. `get_market_data(["bitcoin", "ethereum", "cardano", "solana"])` → Market overview
2. `get_news_feed(["all"])` → Today's crypto news
3. **Claude synthesizes**: *"Markets are mixed today with Bitcoin up X%, driven by news about..."*

### Scenario 4: Multi-Currency Analysis
**User**: *"How much is Bitcoin in EUR and GBP?"*

**Claude's Orchestration**:
1. `get_market_data(["bitcoin"])` → Current USD price
2. `get_currency_rates("USD")` → Exchange rates
3. **Claude synthesizes**: *"Bitcoin is currently $X USD, which equals €Y EUR and £Z GBP..."*

## 📊 **Data Sources**

- **CoinGecko API**: Market data (price, volume, market cap)
- **CryptoPanic API**: Crypto news aggregation
- **Reddit API**: Social sentiment from r/cryptocurrency
- **ExchangeRate-API**: Currency conversion rates

**All APIs are free and require no authentication.**

## 🔍 **Key Features**

### Clean Data Structure
All tools return consistent, well-structured JSON that's easy for LLMs to process.

### Error Handling
Graceful handling of API failures with informative error messages.

### No Analysis in Tools
Tools focus purely on data collection. All analysis and recommendations come from the LLM.

### Rate Limit Friendly
Designed to work within free API tier limits.

## 🧪 **Testing the Strategy**

### What You Should See:
1. **Multiple Tool Calls**: Claude will call 2-4 tools per complex question
2. **Data Synthesis**: Claude combines data from multiple sources
3. **Intelligent Responses**: Claude applies reasoning to raw data
4. **Consistent Logic**: Claude uses trading rules consistently

### What Demonstrates MCP Value:
- **Data Aggregation**: Single MCP call gets data from multiple APIs
- **Error Resilience**: Graceful handling when some APIs fail
- **Structured Output**: Clean, consistent data format for LLM consumption
- **Separation of Concerns**: Clear boundary between data and intelligence

## 📝 **Training Use**




## Best Demo Prompts
1. Investment Decision (Multi-Tool Orchestration)
```
   I have $2000 to invest and I'm considering Bitcoin or Ethereum.
   Which would be better right now? Please analyze the current market
   conditions, recent news, and apply proper risk assessment criteria
   to give me a detailed recommendation with reasoning.
```

2. Market Intelligence (News + Data Synthesis)
```
   What's happening in the crypto markets today? I want to understand
   both the price movements and what's driving them. Give me a
   comprehensive market overview with context.
   ```

3. Global Purchasing Power (Multi-Currency Analysis)
```
   I'm traveling to Europe and Japan next month. If I wanted to buy
   Bitcoin in different countries, how would the purchasing power
   compare? Show me Bitcoin's value in USD, EUR, and JPY with analysis.
```

5. Risk Assessment (Rules Application)
```
   I'm a conservative investor who doesn't like high volatility.
   Based on your trading rules and current market conditions,
   which cryptocurrencies would be appropriate for my risk profile?
   Expected Flow:
```
5. 
6. News Impact Analysis (Advanced Synthesis)
```

   I heard there's been some big news about cryptocurrency regulation.
   How is this affecting Bitcoin and Ethereum prices? Should I be
   concerned about my current holdings?
   Expected Flow:
```
🔥 Pro Demo Prompt (Shows Everything)
```
I'm new to cryptocurrency investing and have $5000 to allocate.
I'm interested in Bitcoin and Ethereum but want to make an informed
decision. Please:

1. Analyze the current market conditions for both assets
2. Review recent news and sentiment
3. Apply proper risk management principles
4. Consider how this investment would look in different currencies
   (I might move to Europe next year)
5. Give me a detailed investment strategy with clear reasoning

I want to understand not just what to do, but WHY based on the data.
```

## 🔧 **Supported Assets**

### Cryptocurrencies
- **Primary**: bitcoin, ethereum, cardano, solana, dogecoin
- **Aliases**: btc→bitcoin, eth→ethereum, ada→cardano, sol→solana, doge→dogecoin

### Fiat Currencies
- **Supported**: USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY
- **Base Options**: USD, EUR, GBP

### News Sources
- **cryptopanic**: Crypto-focused news aggregator
- **reddit**: Social sentiment from r/cryptocurrency
- **all**: Combined data from all sources

## 🚨 **Disclaimer**

This server is for **educational and demonstration purposes only**. It provides market data and tools for analysis but does not constitute financial advice. Always consult with qualified financial advisors before making investment decisions.

## 📞 **Support**

For training workshops and implementation questions, this server demonstrates core MCP patterns that can be adapted to any domain requiring data aggregation and LLM-based analysis.
