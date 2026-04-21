# AutoStream Agent: Social-to-Lead Workflow
(Made for Machine Learning Intern – Assignment
Project
Company: ServiceHive
Product: Inflx
Project Title: Social-to-Lead Agentic Workflow)
AutoStream is a conversational AI assistant designed for content creators. It handles product questions using a local knowledge base (RAG) and collects lead information from interested users. Built with LangGraph, it manages state across multi-turn conversations to ensure a smooth transition from inquiry to lead capture.

## Running Locally

1. **Python Version**: Make sure you have Python 3.9 or newer.
2. **Setup Environment**: 
   - Activate your virtual environment:
     - Windows: `.venv\Scripts\activate`
     - macOS/Linux: `source .venv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`
3. **API Keys**: Create a `.env` file in the root directory. Add your key for Google Gemini, OpenAI, or Anthropic:
   ```env
   GOOGLE_API_KEY=your_key_here
   # OR
   OPENAI_API_KEY=your_key_here
   ```
4. **Launch**: Start the agent by running:
   ```bash
   python main.py
   ```

## Architecture

I chose **LangGraph** for this project because traditional LLM chains are too rigid for sales. In a typical sales conversation, users don't follow a predictable path; they might ask about a feature, go quiet for a bit, then jump straight to wanting a subscription. LangGraph allows the agent to function as a state machine. It can loop, branch, and maintain context across several turns, which is much closer to how humans actually talk. Unlike a linear pipeline that just goes from step A to B, LangGraph lets the agent "think" in cycles—checking if it has enough info to move forward or if it needs to clarify something first.

State management is the backbone of this workflow. We use a central `AgentState` object that acts as a persistent memory for the session. This structure tracks everything from the raw message history to specific extracted data points like the lead's name, email, and preferred platform. Instead of trying to force the LLM to extract all this info in a single prompt, each node in the graph is responsible for one small task—like checking intent or querying our JSON knowledge base. This modular setup means we can update the state incrementally. The agent systematically "fills in the blanks" over multiple exchanges, making the whole process more reliable and less prone to hallucinations than a stateless chatbot.

## WhatsApp Integration

To take this agent from a local terminal to WhatsApp, the architecture would shift to a webhook-driven flow. Here is how I would set it up:

1. **Webhook Registration**: Host a POST `/webhook` endpoint using FastAPI or Flask and register it with the WhatsApp Business Platform.
2. **Message Receipt**: When a user sends a message, WhatsApp hits that endpoint with a JSON payload containing the message details.
3. **Data Extraction**: The server parses the sender’s ID (phone number), the message text, and any session identifiers from the JSON.
4. **State Loading**: We fetch the user's current conversation state from a key-value store like Redis, using their sender ID as the unique key.
5. **Graph Execution**: We feed the loaded state and the new message into the LangGraph agent to generate the appropriate response.
6. **Update & Reply**: Finally, we save the new state back to Redis and send the agent's reply back to the user by POSTing to the WhatsApp API at `graph.facebook.com`.

## Example Flow

**USER**: Hi, tell me about your pricing.
**AGENT**: Hi there! AutoStream offers two main pricing plans to help you with your video needs:

* **Basic Plan:** $29 per month. This includes 10 videos per month at 720p resolution and standard support.
* **Pro Plan:** $79 per month. This includes unlimited videos, 4K resolution, AI captions, and 24/7 support.

Please keep in mind that we have a 7-day refund policy. Let me know if you have any other questions about these options!

**USER**: That sounds great. I make youtube videos-I think the Pro plan is perfect.
**AGENT**: That's a fantastic choice! The Pro plan is definitely the way to go for high-quality YouTube content. 
I'd love to help you get your account set up. To get started, could you please tell me your full name?

**USER**: Rohan Mehta
**AGENT**: Nice to meet you, Rohan Mehta! I’m excited to help you get started with the Pro Plan—it’s going to make your YouTube workflow so much smoother.
To finish setting up your account, could you please provide your email address?

**USER**: rohan@example.com
**AGENT**: Perfect, thanks Rohan! I have your email as rohan@example.com. Just one last thing: could you let me know which platform you primarily create content for? (e.g., YouTube, TikTok, Instagram)

**USER**: I mainly use Youtube to mainly create for
**AGENT**: [Leads to lead capture tool call]
**AGENT**: You're all set, Rohan! Your Pro plan is confirmed. Our team will send a follow-up email to rohan@example.com with all the detail
