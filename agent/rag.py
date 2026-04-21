import json
import os

def load_kb():
    """Loads the knowledge base from the local JSON file."""
    path = os.path.join(os.path.dirname(__file__), "../knowledge_base/autostream_kb.json")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "Knowledge base not found."}

def get_product_info(query: str = None) -> str:
    """Retrieves relevant product information. 
    Since the KB is small, we return the whole context for the LLM to parse.
    """
    kb = load_kb()
    if "error" in kb:
        return kb["error"]
    
    # Format the KB for better LLM readability
    context = "AutoStream Product Information:\n\n"
    
    context += "Pricing Plans:\n"
    for plan in kb.get("pricing", []):
        context += f"- {plan['plan']} Plan: {plan['price']}\n"
        for feature in plan.get("features", []):
            context += f"  * {feature}\n"
            
    context += "\nCompany Policies:\n"
    for policy, detail in kb.get("policies", {}).items():
        context += f"- {policy.capitalize()}: {detail}\n"
        
    return context
