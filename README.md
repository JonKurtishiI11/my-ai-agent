# My AI Agent Kaggle 5-Day ADK Course

Built with Google's Agent Development Kit (ADK) and Claude (Anthropic).

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/JonKurtishiI11/my-ai-agent.git
cd my-ai-agent
```

**2. Create and activate virtual environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create a `.env` file** in the root folder next to `my_agent/` and add:
```
ANTHROPIC_API_KEY=your_anthropic_key_here
```

**5. Run**
```bash
adk web
```

Open `http://localhost:8000` in your browser.

## Tools

**ADK built-in**

`load_memory` searches past conversation logs to recall context from previous sessions.

**Custom tools**

Weather fetches live conditions for any city. Math handles advanced calculations including sqrt, powers and percentages. Unit converter supports km/miles, kg/lbs and celsius/fahrenheit. Notes saves and retrieves notes across sessions. Tasks saves items with priority and due date. User profile permanently stores your name, city, job and goals so the agent remembers you across all sessions.

**Fitness tools**

Workout planner generates structured plans for chest, back, legs, shoulders, arms and full body. Workout logger records exercises with sets, reps and weight. Progress tracker shows history and personal records. Body metrics calculates BMI, BMR, daily calories and protein targets for muscle building.

## Project structure

```
my_agent/
├── agent.py              # Main coordinator and all specialist agents
├── architectures.py      # Sequential, Parallel and Loop agent patterns
├── session_agent.py      # Short-term session memory demo
├── memory_agent.py       # Long-term memory across sessions demo
├── observability.py      # Logs, traces and metrics demo
├── evaluation.py         # LLM-as-a-Judge evaluation pipeline
├── multi_agent.py        # Multi-agent coordinator demo
└── tools/
    ├── advanced_tools.py # Weather, notes, tasks, user profile, converter
    └── fitness_tools.py  # Workout planner, logger and body metrics
```
