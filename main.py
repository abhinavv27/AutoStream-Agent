import os
import sys
from dotenv import load_dotenv

# Fix for Windows terminal encoding issues
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from agent.graph import create_agent_graph

def get_llm():
    """Initializes the LLM based on available environment variables."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return ChatAnthropic(model="claude-3-haiku-20240307")
    elif os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-4o-mini")
    elif os.getenv("GOOGLE_API_KEY"):
        return ChatGoogleGenerativeAI(model="gemini-flash-latest")
    else:
        raise ValueError("No API key found. Please set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY in .env")

def print_header():
    print("\n" + "="*50)
    print("   AUTOSTREAM CONVERSATIONAL AI AGENT")
    print("   Social-to-Lead Agentic Workflow")
    print("="*50)
    print("Type 'exit' or 'quit' to end the session.\n")

def main():
    load_dotenv()
    
    try:
        llm = get_llm()
    except ValueError as e:
        print(f"Error: {e}")
        return

    graph = create_agent_graph()
    
    # Initialize state
    state = {
        "messages": [],
        "intent": None,
        "lead_name": None,
        "lead_email": None,
        "lead_platform": None,
        "lead_captured": False
    }
    
    print_header()
    
    while True:
        user_input = input("USER: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("AGENT: Goodbye! Have a great day creating content.")
            break
            
        # Add user message to state
        state["messages"].append(HumanMessage(content=user_input))
        
        # Run the graph
        # We pass the llm in the config so nodes can access it
        config = {"configurable": {"llm": llm}}
        
        try:
            output = graph.invoke(state, config=config)
            
            # Update state with the output from the graph
            state = output
            
            # Print the last message from the agent
            if state["messages"]:
                last_message = state["messages"][-1]
                content = last_message.content
                if isinstance(content, list):
                    # Handle structured content (e.g. from Gemini)
                    text_parts = [part.get("text", "") for part in content if isinstance(part, dict) and part.get("type") == "text"]
                    print(f"AGENT: {''.join(text_parts)}\n")
                else:
                    print(f"AGENT: {content}\n")
                
        except Exception as e:
            print(f"\n[ERROR] Something went wrong: {e}")
            print("Please check your API keys and internet connection.\n")

if __name__ == "__main__":
    main()
