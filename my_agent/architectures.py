from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent

def analyze_text(text: str) -> dict:
    """Analyzes a piece of text and returns word count and basic stats.
    
    Args:
        text: The text to analyze.
    
    Returns:
        A dict with word count, character count, and sentence count.
    """
    words = text.split()
    sentences = text.count('.') + text.count('!') + text.count('?')
    return {
        "word_count": len(words),
        "char_count": len(text),
        "sentence_count": max(sentences, 1)
    }

def summarize_text(text: str) -> dict:
    """Creates a short summary of the text.
    
    Args:
        text: The text to summarize.
    
    Returns:
        A dict with a one-line summary.
    """
    words = text.split()
    short = " ".join(words[:20])
    return {"summary": f"{short}..." if len(words) > 20 else text}

def check_tone(text: str) -> dict:
    """Checks the tone of a text (positive, negative, neutral).
    
    Args:
        text: The text to check.
    
    Returns:
        A dict with detected tone.
    """
    positive_words = ["good", "great", "excellent", "happy", "love", "best"]
    negative_words = ["bad", "terrible", "hate", "worst", "awful", "poor"]
    text_lower = text.lower()
    pos = sum(1 for w in positive_words if w in text_lower)
    neg = sum(1 for w in negative_words if w in text_lower)
    tone = "positive" if pos > neg else "negative" if neg > pos else "neutral"
    return {"tone": tone, "positive_signals": pos, "negative_signals": neg}


single_agent = Agent(
    model="claude-sonnet-4-5",
    name="single_agent",
    description="A single agent that analyzes text.",
    instruction="""
    You analyze text when given to you.
    Use your tools to get stats, summary and tone.
    Present results clearly.
    """,
    tools=[analyze_text, summarize_text, check_tone],
)


analyst_agent = Agent(
    model="claude-sonnet-4-5",
    name="analyst_agent",
    description="Analyzes text statistics.",
    instruction="Analyze the text given to you. Use analyze_text tool and report the stats.",
    tools=[analyze_text],
)

summarizer_agent = Agent(
    model="claude-sonnet-4-5",
    name="summarizer_agent",
    description="Summarizes text.",
    instruction="Summarize the text given to you using the summarize_text tool.",
    tools=[summarize_text],
)

tone_agent = Agent(
    model="claude-sonnet-4-5",
    name="tone_agent",
    description="Checks tone of text.",
    instruction="Check the tone of the text using check_tone tool and explain what it means.",
    tools=[check_tone],
)

sequential_pipeline = SequentialAgent(
    name="sequential_pipeline",
    description="Analyzes text step by step: stats → summary → tone.",
    sub_agents=[analyst_agent, summarizer_agent, tone_agent],
)

parallel_pipeline = ParallelAgent(
    name="parallel_pipeline",
    description="Runs text analysis, summary and tone check all at once.",
    sub_agents=[analyst_agent, summarizer_agent, tone_agent],
)


refinement_agent = Agent(
    model="claude-sonnet-4-5",
    name="refinement_agent",
    description="Keeps refining a summary until it is under 10 words.",
    instruction="""
    You receive a text and must produce a summary under 10 words.
    Use summarize_text to get a draft summary.
    If it is longer than 10 words, shorten it yourself.
    When done, say DONE and give the final summary.
    """,
    tools=[summarize_text],
)

loop_pipeline = LoopAgent(
    name="loop_pipeline",
    description="Refines a summary iteratively.",
    sub_agents=[refinement_agent],
    max_iterations=3,
)