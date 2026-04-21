# AutoStream Conversational AI Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a multi-turn sales agent for AutoStream that handles product inquiries via RAG and captures leads for high-intent users using LangGraph.

**Architecture:** A state-driven agent using LangGraph to route conversations based on intent. It retrieves product data from a local JSON KB and manages lead collection fields (name, email, platform) before firing a mock tool.

**Tech Stack:** Python, LangChain, LangGraph, Claude 3 Haiku / GPT-4o-mini / Gemini 1.5 Flash.

---

### Task 1: Environment Setup & Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `.env`

**Step 1: Define dependencies**
Write the following to `requirements.txt`:
```text
langchain>=0.2.0
langgraph>=0.1.0
langchain-anthropic>=0.1.0
langchain-openai>=0.1.0
langchain-google-genai>=0.1.0
python-dotenv>=1.0.0
```

**Step 2: Create .env template**
```text
# Choose one and fill in
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

**Step 3: Commit**
```bash
git add requirements.txt .env
git commit -m "chore: initial environment setup"
```

---

### Task 2: Knowledge Base Creation

**Files:**
- Create: `knowledge_base/autostream_kb.json`

**Step 1: Populate KB with pricing and policies**
```json
{
  "pricing": [
    {
      "plan": "Basic",
      "price": "$29/month",
      "features": ["10 videos per month", "720p resolution", "Standard support"]
    },
    {
      "plan": "Pro",
      "price": "$79/month",
      "features": ["Unlimited videos", "4K resolution", "AI captions", "24/7 support"]
    }
  ],
  "policies": {
    "refunds": "No refunds after 7 days",
    "support": "24/7 support available on Pro plan only"
  }
}
```

**Step 2: Commit**
```bash
git add knowledge_base/autostream_kb.json
git commit -m "feat: add knowledge base"
```

---

### Task 3: RAG Retrieval Module

**Files:**
- Create: `agent/rag.py`

**Step 1: Implement basic KB loader and search**
```python
import json
import os

def load_kb():
    path = os.path.join(os.path.dirname(__file__), "../knowledge_base/autostream_kb.json")
    with open(path, "r") as f:
        return json.load(f)

def get_product_info(query: str) -> str:
    kb = load_kb()
    return json.dumps(kb, indent=2)
```

**Step 2: Commit**
```bash
git add agent/rag.py
git commit -m "feat: implement RAG retrieval module"
```

---

### Task 4: Intent Classification Logic

**Files:**
- Create: `agent/intent.py`

**Step 1: Define Intent Classification prompt and function**
```python
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

INTENT_PROMPT = """Classify the user's latest message into one of three categories:
1. 'greeting': Casual hello or generic opener.
2. 'inquiry': Questions about features, pricing, or policies.
3. 'lead': Signals readiness to buy or get started (e.g., 'I want to sign up', 'I'll take the Pro plan').

User message: {message}

Return ONLY the category name."""

def classify_intent(message: str, llm) -> Literal["greeting", "inquiry", "lead"]:
    prompt = ChatPromptTemplate.from_template(INTENT_PROMPT)
    chain = prompt | llm | StrOutputParser()
    intent = chain.invoke({"message": message}).strip().lower()
    if intent in ["greeting", "inquiry", "lead"]:
        return intent
    return "inquiry" # Default
```

**Step 2: Commit**
```bash
git add agent/intent.py
git commit -m "feat: add intent classification logic"
```

---

### Task 5: Mock Lead Capture Tool

**Files:**
- Create: `agent/tools.py`

**Step 1: Implement the mock API**
```python
def mock_lead_capture(name: str, email: str, platform: str):
    """Captures lead info and returns a success status."""
    print(f"\n[SYSTEM] Lead captured: {name}, {email}, {platform}")
    return {'status': 'success', 'lead_id': 'LEAD_001'}
```

**Step 2: Commit**
```bash
git add agent/tools.py
git commit -m "feat: add mock lead capture tool"
```

---

### Task 6: LangGraph State Graph Implementation

**Files:**
- Create: `agent/graph.py`

**Step 1: Define State and Graph Nodes**
Implement the `AgentState` TypedDict and the nodes: `classify`, `handle_greeting`, `handle_inquiry`, `handle_lead_collection`.

**Step 2: Define Conditional Edges**
Route based on `state["intent"]`.

**Step 3: Commit**
```bash
git add agent/graph.py
git commit -m "feat: implement LangGraph agentic workflow"
```

---

### Task 7: CLI Entry Point

**Files:**
- Create: `main.py`

**Step 1: Implement REPL loop**
Load environment variables, initialize LLM, initialize graph, and start loop.

**Step 2: Commit**
```bash
git add main.py
git commit -m "feat: add CLI entry point"
```

---

### Task 8: Professional README & Documentation

**Files:**
- Create: `README.md`

**Step 1: Write comprehensive documentation**
Include setup, architecture (LangGraph), WhatsApp plan, and example transcript.

**Step 2: Commit**
```bash
git add README.md
git commit -m "docs: finalize project documentation"
```
