# Autonomous Agent with Long-Term Memory

An autonomous AI agent with long-term memory capabilities using Azure Cosmos DB for vector-based semantic search. The agent remembers past interactions, learns from similar situations, and maintains conversation context across sessions.

## 🌟 Features

- 🧠 **Long-Term Memory**: Stores every interaction in Azure Cosmos DB with vector embeddings
- 🔍 **Semantic Search**: Finds similar past interactions using cosine similarity
- 📝 **Conversation History**: Maintains last 5 conversations per session for context continuity
- 🤖 **Autonomous Planning**: Creates and executes multi-step plans to achieve goals
- 🔧 **MCP Integration**: Uses Model Context Protocol for extensible tool access
- 💭 **Self-Reflection**: Evaluates execution success and learns from outcomes
- ⚡ **Serverless Ready**: Works with Azure Cosmos DB Serverless (pay-per-use)
- 🎯 **Context-Aware**: Uses past interactions to provide more intelligent responses

## 🏗️ Architecture

```txt
┌─────────────────────────────────────────────────────────────┐
│                      User Query                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Memory Store (Azure Cosmos DB)                  │
│  • Retrieve last 5 conversations (session history)           │
│  • Find 3 similar past interactions (vector search)          │
│  • Generate embeddings (OpenAI text-embedding-3-small)       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Planner Agent                               │
│  • Considers conversation history                            │
│  • Learns from similar past interactions                     │
│  • Generates structured plan (JSON steps)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Executor Agent                              │
│  • Executes plan steps sequentially                          │
│  • Uses MCP tools (Calculator, Weather API)                  │
│  • Records observations from each step                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                Reflector Agent                               │
│  • Analyzes execution results                                │
│  • Compares with similar past successes                      │
│  • Decides: CONTINUE / RETRY / FAIL                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Store Interaction in Memory                     │
│  • Goal, Plan, Observations, Result                          │
│  • Generate 1536-dim embedding for semantic search           │
│  • Store with timestamp and session ID                       │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
agentic-ai-w-fastmcp/
├── agent/
│   ├── __init__.py
│   ├── autonomous.py      # Main agent orchestration with memory
│   ├── planner.py         # Context-aware plan generation
│   ├── executor.py        # Plan execution with observations
│   ├── reflector.py       # Execution evaluation
│   ├── state.py           # Agent state with session tracking
│   └── memory.py          # Memory store (Cosmos DB + embeddings)
├── client.py              # Interactive CLI client
├── server.py              # MCP server with tools (Calculator, Weather)
├── pyproject.toml         # Project dependencies
├── .env.example           # Environment variables template
├── test_agent.py          # Comprehensive test suite
├── test_memory.py         # Memory store testing
├── verify_setup.py        # Setup verification script
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.12+**
2. **OpenAI API Key** - For embeddings and LLM
3. **Azure Cosmos DB** - Serverless or Provisioned (SQL API)

### 1. Azure Cosmos DB Setup

#### Option A: Create New Cosmos DB (Serverless - Recommended)

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **Create a resource** → **Azure Cosmos DB**
3. Select **Azure Cosmos DB for NoSQL**
4. Choose:
   - **Capacity mode**: Serverless (pay-per-use, ~$0.01/month for 1000 queries)
   - **Location**: Choose closest to you
5. After creation, go to **Keys** section
6. Copy:
   - **URI** (your endpoint)
   - **PRIMARY KEY**

#### Option B: Use Existing Cosmos DB

If you already have Cosmos DB (like yours):

- Endpoint: `https://hdm-vectordb-cos-eastus2-xxx.documents.azure.com:443/`
- Just get your key from Azure Portal → Cosmos DB → Keys

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# OpenAI API Key (Required)
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Azure Cosmos DB SQL API Configuration (Required)
COSMOS_ENDPOINT=https://your-account-name.documents.azure.com:443/
COSMOS_KEY=your_primary_key_here==
COSMOS_DATABASE=agent_memory
```

### 3. Install Dependencies

```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

### 4. Verify Setup

```bash
python verify_setup.py
```

This checks:

- ✅ Python version (3.12+)
- ✅ All dependencies installed
- ✅ Environment variables configured
- ✅ Project structure complete

### 5. Run Tests (Optional but Recommended)

```bash
# Test memory store only
python test_memory.py

# Test full agent system
python test_agent.py
```

### 6. Start the System

**Terminal 1** - Start MCP Server:

```bash
uv run server.py
```

Output should show:

```
INFO - Starting MCP server on port 8000...
```

**Terminal 2** - Start Agent Client:

```bash
uv run client.py
```

## 💬 Usage Examples

### Basic Queries

```
You: what is 25 * 48?
Agent: The result of 25 * 48 is 1200

You: what's the weather in bengaluru?
Agent: The current temperature in Bengaluru is 27.6°C
```

### Context-Aware Conversations

```
You: what's the temperature in paris?
Agent: The current temperature in Paris is 8°C

You: and in london?
Agent: The current temperature in London is 10°C

You: which one is warmer?
Agent: London is warmer at 10°C compared to Paris at 8°C

You: should i carry a jacket in the warmer city?
Agent: [Remembers London is warmer] At 10°C in London, yes, you should carry a jacket as it's quite cold.
```

### Session Management

```
You: session
Current session ID: d7256db3-6a67-4214-8113-8d9b4dc1c316

You: new
Started new session: 5f23c430-b1f3-4ab2-9d91-ec03987c2016

You: exit
Goodbye! 👋
```

## 🧠 How Memory Works

### 1. Storing Interactions

Every interaction is stored with:

- **Goal**: User's query
- **Plan**: Generated step-by-step plan
- **Observations**: Execution results from each step
- **Result**: Final answer
- **Embedding**: 1536-dimensional vector (OpenAI text-embedding-3-small)
- **Metadata**: Session ID, timestamp, decision, custom tags

Example document in Cosmos DB:

```json
{
  "id": "session-123_1706400000.123",
  "session_id": "session-123",
  "timestamp": "2026-01-28T10:30:00Z",
  "goal": "what's the weather in paris?",
  "plan": ["Get weather for Paris", "Format response"],
  "observations": ["Temperature is 8°C"],
  "result": "The current temperature in Paris is 8°C",
  "embedding": [0.123, -0.456, ..., 0.789],
  "metadata": {"decision": "CONTINUE", "steps_executed": 2}
}
```

### 2. Retrieving Context

For each new query, the agent retrieves:

**A. Recent History (Last 5 in session)**

- Same session_id only
- Chronological order
- Maintains conversation flow
- Example: "that city" → knows which city from previous query

**B. Similar Interactions (Top 3 across all sessions)**

- Uses vector similarity search
- Finds semantically similar past queries
- Learns from successful strategies
- Example: "Paris temperature" finds "weather in Paris" from months ago

### 3. Vector Similarity Search

The system uses **cosine similarity** to find related interactions:

```
Query: "temperature in paris"
→ Embedding: [0.1, 0.2, 0.3, ..., 0.9]

Stored Interactions:
1. "weather in paris"     → Similarity: 0.95 ✅ Very similar!
2. "paris forecast"       → Similarity: 0.88 ✅ Similar
3. "tokyo temperature"    → Similarity: 0.75 ✅ Somewhat similar
4. "calculate 2+2"        → Similarity: 0.12 ❌ Not relevant

Returns top 3 most similar interactions
```

### 4. Search Methods

The system intelligently uses multiple search methods:

**Level 1: Native VectorDistance (Fastest)**

- Uses Cosmos DB's built-in `VectorDistance()` function
- Requires container with vector indexing policy
- Falls back if not available

**Level 2: Manual Cosine Similarity (Reliable)**

- Fetches data and calculates similarity using numpy
- Works with any Cosmos DB configuration
- **This is what you're currently using** ✅
- Fast enough for up to 10,000 interactions

**Level 3: Recent Items (Fallback)**

- Returns most recent interactions
- No similarity calculation
- Always works

## 🎯 Client Commands

| Command           | Description                                 |
| ----------------- | ------------------------------------------- |
| `<your question>` | Ask the agent anything                      |
| `session`         | View current session ID                     |
| `new` or `reset`  | Start a new session (clears recent history) |
| `exit` or `quit`  | Exit the application                        |

## 🔧 MCP Tools Available

The agent has access to these tools via MCP:

### Calculator

```python
calculate("25 * 48")  # Returns: "The result of 25 * 48 is 1200"
```

### Weather

```python
get_weather("Paris")  # Returns: "The current temperature in Paris is 8°C"
```

### Adding Custom Tools

Edit `server.py` to add more tools:

```python
@mcp.tool()
async def my_custom_tool(param: str) -> str:
    """Description of what the tool does."""
    # Your implementation here
    return result
```

## ⚙️ Configuration

### Memory Settings

Adjust context retrieval in `agent/autonomous.py`:

```python
context = await memory.get_relevant_context(
    goal=goal,
    session_id=state.session_id,
    history_limit=5,      # Recent history count
    similar_limit=3,      # Similar interactions count
)
```

### Embedding Model

Change in `agent/memory.py`:

```python
response = await self.openai_client.embeddings.create(
    model="text-embedding-3-small",  # or "text-embedding-3-large"
    input=text
)
```

### Database Names

Set in `.env` or pass to MemoryStore:

```python
memory = MemoryStore(
    database_name="my_custom_db",
    collection_name="my_conversations"
)
```

## 💰 Cost Estimation

### Azure Cosmos DB Serverless

**Storage**: $0.25 per GB/month

- Each interaction: ~2 KB
- 1,000 interactions: ~2 MB
- Cost: ~$0.0005/month

**Operations**: $0.285 per million RU

- Store interaction: ~10 RU
- Vector search: ~30-50 RU
- 1,000 interactions/month: ~$0.009/month

### OpenAI API

**Embeddings**: $0.00002 per 1K tokens (text-embedding-3-small)

- ~100 tokens per interaction
- 1,000 interactions: ~$0.002/month

**LLM**: $0.150 per 1M input tokens, $0.600 per 1M output tokens (gpt-4o-mini)

- Varies by query complexity
- Estimate: ~$0.50-2.00 per 1,000 queries

### Total Estimated Cost

For 1,000 interactions/month:

- Cosmos DB: ~$0.01
- OpenAI Embeddings: ~$0.002
- OpenAI LLM: ~$0.50-2.00
- **Total: ~$0.51-2.01/month**

Very affordable for development and small-scale production!

## 📊 Monitoring

### Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Cosmos DB account
3. Click **Data Explorer**
4. Browse: `agent_memory` → `conversations`
5. View stored interactions and embeddings

### Cost Management

1. Azure Portal → Cosmos DB → Metrics
2. Check:
   - Request Units (RU) consumed
   - Storage usage
   - Request count

3. Azure Portal → Cost Management
   - See daily costs
   - Set budget alerts

### Logging

View logs in the terminal where server/client are running. Adjust log level in `client.py`:

```python
# Show more details (INFO level)
logging.basicConfig(level=logging.INFO)

# Show only errors (default)
logging.basicConfig(level=logging.ERROR)
```

## 🧪 Testing

### Quick Tests

```bash
# Test memory store only
python test_memory.py

# Test full agent system
python test_agent.py
```

### Manual Testing

```bash
# Terminal 1
uv run server.py

# Terminal 2
uv run client.py
```

Test scenarios:

1. **Basic query**: "what is 10 + 5?"
2. **Follow-up**: "multiply that by 2"
3. **New session**: Type `new`, then "multiply that by 2" (should not have context)
4. **Similar query**: Ask about weather in different cities

## 🐛 Troubleshooting

### "Failed to connect to Cosmos DB"

**Check 1**: Verify credentials in `.env`

```bash
python check_config.py
```

**Check 2**: Test connection

```bash
python test_memory.py
# Choose option 2
```

**Check 3**: Verify firewall rules in Azure Portal

- Cosmos DB → Networking
- Add your IP address or allow all networks

### "Module not found" errors

```bash
# Reinstall dependencies
uv pip install -e .

# Or
pip install -e . --force-reinstall
```

### "MCP server not responding"

**Check 1**: Is server running?

```bash
# Look for this message:
INFO - Starting MCP server on port 8000...
```

**Check 2**: Port already in use?

```bash
lsof -i :8000
# Kill the process if needed
```

**Check 3**: Restart server

```bash
# Ctrl+C to stop, then restart:
uv run server.py
```

### "Vector search warnings"

The warning `SQL API vector search failed` is **normal and expected**. The system automatically falls back to manual similarity search which works perfectly fine. This warning is suppressed in the latest version.

If you still see it:

```bash
# Check logging configuration in client.py
grep "logging.basicConfig" client.py
```

### Performance Issues

**Slow similarity search**:

- Expected with 10,000+ interactions
- Consider:
  - Enabling native vector search with proper indexing
  - Upgrading to provisioned throughput
  - Implementing caching

**High costs**:

- Check Azure Portal → Cost Management
- Reduce `history_limit` and `similar_limit` in config
- Use smaller embedding model

## 🔒 Security Best Practices

1. **Never commit `.env` file**

   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use Azure Key Vault** (Production)

   ```python
   from azure.keyvault.secrets import SecretClient
   cosmos_key = secret_client.get_secret("cosmos-key").value
   ```

3. **Rotate API keys regularly**
   - OpenAI Dashboard → API Keys
   - Azure Portal → Cosmos DB → Keys

4. **Set up firewall rules**
   - Azure Portal → Cosmos DB → Networking
   - Restrict to specific IPs

5. **Enable private endpoints** (Production)
   - Azure Portal → Cosmos DB → Private endpoints

## 🚀 Production Deployment

### Environment Variables

Set these on your server:

```bash
export OPENAI_API_KEY="sk-..."
export COSMOS_ENDPOINT="https://..."
export COSMOS_KEY="..."
export COSMOS_DATABASE="agent_memory"
```

### Run with Systemd (Linux)

Create `/etc/systemd/system/agent-server.service`:

```ini
[Unit]
Description=Agent MCP Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/project
Environment="OPENAI_API_KEY=sk-..."
Environment="COSMOS_ENDPOINT=https://..."
Environment="COSMOS_KEY=..."
ExecStart=/usr/bin/uv run server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable agent-server
sudo systemctl start agent-server
```

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv pip install -e .

CMD ["uv", "run", "server.py"]
```

Build and run:

```bash
docker build -t agent-server .
docker run -e OPENAI_API_KEY=sk-... -e COSMOS_ENDPOINT=https://... -p 8000:8000 agent-server
```

## 📚 Additional Resources

- [Azure Cosmos DB Documentation](https://learn.microsoft.com/en-us/azure/cosmos-db/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

## 🙏 Acknowledgments

- Built with [Pydantic AI](https://ai.pydantic.dev/)
- MCP server powered by [FastMCP](https://github.com/jlowin/fastmcp)
- Vector storage via [Azure Cosmos DB](https://azure.microsoft.com/products/cosmos-db/)
- Embeddings by [OpenAI](https://openai.com/)
