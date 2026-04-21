from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

INTENT_PROMPT = """Classify the user's latest message into one of three categories:
1. 'greeting': Casual hello or generic opener.
2. 'inquiry': Questions about features, pricing, or policies.
3. 'lead': Signals readiness to buy, get started, or choosing a specific plan (e.g., 'I want to sign up', 'I'll take the Pro plan', 'How do I start?').

User message: {message}

Return ONLY the category name: greeting, inquiry, or lead. No other text."""

def classify_user_intent(message: str, llm) -> Literal["greeting", "inquiry", "lead"]:
    """Classifies the user's intent using the provided LLM."""
    prompt = ChatPromptTemplate.from_template(INTENT_PROMPT)
    chain = prompt | llm | StrOutputParser()
    intent = chain.invoke({"message": message}).strip().lower()
    
    # Validation and fallback
    if intent in ["greeting", "inquiry", "lead"]:
        return intent
    
    # Heuristic fallback if LLM output is messy
    if any(word in intent for word in ["sign up", "start", "buy", "pro plan", "basic plan"]):
        return "lead"
    if any(word in intent for word in ["how", "price", "cost", "feature", "video"]):
        return "inquiry"
        
    return "greeting"
