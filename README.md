# My AI Agent Kaggle 5-Day ADK Course

Built with Google's Agent Development Kit (ADK) and Claude (Anthropic).

## What's inside

| File | Day | Description |
|---|---|---|
| `my_agent/agent.py` | Day 1-5 | Main coordinator agent with specialists |
| `my_agent/architectures.py` | Day 1b | Sequential, Parallel, Loop agents |
| `my_agent/tools/advanced_tools.py` | Day 2 | Weather, notes, calculator, unit converter |
| `my_agent/session_agent.py` | Day 3a | Short-term session memory |
| `my_agent/memory_agent.py` | Day 3b | Long-term memory across sessions |
| `my_agent/observability.py` | Day 4a | Logs, traces, metrics, callbacks |
| `my_agent/evaluation.py` | Day 4b | LLM-as-a-Judge evaluation pipeline |
| `my_agent/multi_agent.py` | Day 5 | Multi-agent coordinator with A2A pattern |

## Setup

1. Clone the repo
2. Create virtual environment: `python -m venv .venv`
3. Activate: `.venv\Scripts\activate`
4. Install: `pip install google-adk[extensions] anthropic httpx`
5. Create `.env` file with your API key:

6. Run: `adk web`

## Agent capabilities

- Live weather for any city
- Math and unit conversions
- Task and note saving
- Long-term memory across sessions
- Full observability with logs and traces
- LLM-as-a-Judge evaluation
- Multi-agent coordinator pattern
