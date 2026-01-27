# Documentation

## Understanding MCP Architecture

```txt
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│   MCP Host      │◄───────►│   MCP Client    │◄───────►│   MCP Server    │
│   (Claude App)  │         │   (Protocol)    │         │   (Your Tools)  │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

- **MCP Host** are AI application (like Claude Desktop, IDEs, or custom apps) that need to access external context.
- **MCP Clients** maintain connections to servers and handle the protocol communication.
- **MCP Servers** are lightweight programs you build that expose specific capabilities to the AI.

## High-level architecture

```txt
User Goal
   ↓
Planner Agent  ──→  Structured Plan (steps)
   ↓
Executor Agent ──→  Tool calls via MCP
   ↓
State / Memory
   ↓
Critic / Reflector Agent
   ↓
Continue or Finish
```

## Test

```bash
uv run client.py
Autonomous Agent (type 'exit' to quit)

You: what's double the current temperature in bengaluru?
Agent: Double the current temperature in Bengaluru is 53.0°C.

You: should i carry a jacket in bengaluru today ?
Agent: The current temperature in Bengaluru is 26.5°C. Generally, temperatures below 20°C may warrant carrying a jacket. Since 26.5°C is relatively warm, it likely doesn't require a jacket.

You: is today colder than yesterday in bengaluru ?
Agent: The current temperature in Bengaluru is still 26.5°C. Unfortunately, I don't have the temperature data for yesterday to compare. Is there anything else you would like to know?

You: keep calculating the temperature in bengaluru until it changes ?
Agent: The current temperature in Bengaluru is still 26.5°C, which is consistent with previous observations. Since there is no change in the temperature, I will repeat from step 3. Please confirm how you would like to proceed or if you want to continue observing the temperature.

You: yes continue
Traceback (most recent call last):
  File "/home/linux-dex/Documents/HDM/Agentic-AI/agentic_ai_w_fastmcp/client.py", line 21, in <module>
    asyncio.run(main())
  File "/home/linux-dex/.local/share/uv/python/cpython-3.12.11-linux-x86_64-gnu/lib/python3.12/asyncio/runners.py", line 195, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/home/linux-dex/.local/share/uv/python/cpython-3.12.11-linux-x86_64-gnu/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/linux-dex/.local/share/uv/python/cpython-3.12.11-linux-x86_64-gnu/lib/python3.12/asyncio/base_events.py", line 691, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/home/linux-dex/Documents/HDM/Agentic-AI/agentic_ai_w_fastmcp/client.py", line 16, in main
    result = await run_autonomous_agent(goal)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/linux-dex/Documents/HDM/Agentic-AI/agentic_ai_w_fastmcp/agent/autonomous.py", line 33, in run_autonomous_agent
    return state.observations[-1]
           ~~~~~~~~~~~~~~~~~~^^^^
IndexError: list index out of range
```
