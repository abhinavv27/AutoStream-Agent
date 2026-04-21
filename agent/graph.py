from typing import TypedDict, Optional, List, Annotated, Literal
from operator import add
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from agent.intent import classify_user_intent
from agent.rag import get_product_info
from agent.tools import mock_lead_capture

# State definition
class AgentState(TypedDict):
    # The list of messages in the conversation
    # We use add to append new messages to the existing list
    messages: Annotated[List[BaseMessage], add]
    intent: Optional[str]         # 'greeting' | 'inquiry' | 'lead'
    lead_name: Optional[str]
    lead_email: Optional[str]
    lead_platform: Optional[str]
    lead_captured: bool           # True after tool fires

# --- Nodes ---

def classify_intent_node(state: AgentState, config):
    llm = config["configurable"]["llm"]
    latest_message = state["messages"][-1].content
    intent = classify_user_intent(latest_message, llm)
    return {"intent": intent}

def handle_greeting_node(state: AgentState, config):
    llm = config["configurable"]["llm"]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a friendly assistant for AutoStream, a video editing SaaS. Greet the user warmly and ask how you can help them today with their video content."),
        ("placeholder", "{messages}")
    ])
    chain = prompt | llm
    response = chain.invoke(state)
    return {"messages": [response]}

def handle_inquiry_node(state: AgentState, config):
    llm = config["configurable"]["llm"]
    context = get_product_info()
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a helpful AutoStream sales assistant. Use the following context to answer the user's question. If the answer is not in the context, politely say you don't know and offer to connect them with a human.\n\nContext:\n{context}"),
        ("placeholder", "{messages}")
    ])
    chain = prompt | llm
    response = chain.invoke(state)
    return {"messages": [response]}

def handle_lead_collection_node(state: AgentState, config):
    llm = config["configurable"]["llm"]
    
    # Simple extraction logic using LLM
    extraction_prompt = f"""Extract lead information from the conversation history. 
    If a field is already provided in the state, keep it. 
    If it's in the latest message, update it.
    
    Current State:
    Name: {state.get('lead_name')}
    Email: {state.get('lead_email')}
    Platform: {state.get('lead_platform')}
    
    Latest message: {state['messages'][-1].content}
    
    Return ONLY a JSON with keys: name, email, platform. Use null if not found."""
    
    extraction_response = llm.invoke([HumanMessage(content=extraction_prompt)])
    import json
    try:
        # Simple cleanup in case LLM adds markdown
        content = extraction_response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        data = json.loads(content)
        
        updates = {}
        if data.get("name") and not state.get("lead_name"): updates["lead_name"] = data["name"]
        if data.get("email") and not state.get("lead_email"): updates["lead_email"] = data["email"]
        if data.get("platform") and not state.get("lead_platform"): updates["lead_platform"] = data["platform"]
        
        # If we have updates, we still need to generate a response to the user
        # We'll merge updates into state for the response generation
        current_state = {**state, **updates}
    except:
        current_state = state
        updates = {}

    # Check what's missing
    missing = []
    if not current_state.get("lead_name"): missing.append("full name")
    if not current_state.get("lead_email"): missing.append("email address")
    if not current_state.get("lead_platform"): missing.append("creator platform (YouTube, Instagram, etc.)")
    
    if not missing:
        # All fields collected, we'll route to capture next
        return {**updates, "messages": [AIMessage(content="Perfect! I have all the details. Let me get you set up right now...")]}
    
    # Ask for the next missing field
    next_field = missing[0]
    response_prompt = f"The user wants to sign up for AutoStream. We have: Name={current_state.get('lead_name')}, Email={current_state.get('lead_email')}, Platform={current_state.get('lead_platform')}. Please ask the user for their {next_field} in a friendly way."
    
    response = llm.invoke([SystemMessage(content=response_prompt)] + current_state["messages"])
    return {**updates, "messages": [response]}

def capture_lead_node(state: AgentState, config):
    # Call the tool
    result = mock_lead_capture(
        state["lead_name"], 
        state["lead_email"], 
        state["lead_platform"]
    )
    
    response = AIMessage(content=f"You’re all set, {state['lead_name']}! Our team will reach out at {state['lead_email']} shortly to help you get started with AutoStream.")
    return {"lead_captured": True, "messages": [response]}

# --- Routing ---

def route_after_classify(state: AgentState):
    if state["intent"] == "greeting":
        return "greeting"
    elif state["intent"] == "lead" or state.get("lead_name") or state.get("lead_email") or state.get("lead_platform"):
        # If we have any lead data, keep collecting until done
        return "lead_collection"
    else:
        return "inquiry"

def route_after_collection(state: AgentState):
    if state.get("lead_name") and state.get("lead_email") and state.get("lead_platform"):
        return "capture"
    return END

# --- Build Graph ---

def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("classify", classify_intent_node)
    workflow.add_node("greeting", handle_greeting_node)
    workflow.add_node("inquiry", handle_inquiry_node)
    workflow.add_node("lead_collection", handle_lead_collection_node)
    workflow.add_node("capture", capture_lead_node)
    
    workflow.set_entry_point("classify")
    
    workflow.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "greeting": "greeting",
            "inquiry": "inquiry",
            "lead_collection": "lead_collection"
        }
    )
    
    workflow.add_edge("greeting", END)
    workflow.add_edge("inquiry", END)
    
    workflow.add_conditional_edges(
        "lead_collection",
        route_after_collection,
        {
            "capture": "capture",
            END: END
        }
    )
    
    workflow.add_edge("capture", END)
    
    return workflow.compile()
