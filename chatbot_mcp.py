import os
import logging
import uuid
from dotenv import load_dotenv
import gradio as gr
from pymongo import MongoClient

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain.agents import create_agent
from langgraph.checkpoint.mongodb import MongoDBSaver

# --- 1. Setup ---
logging.getLogger("langchain_google_genai").setLevel(logging.ERROR)
load_dotenv(dotenv_path='.env')

google_api_key = os.getenv("GOOGLE_API_KEY")
mongo_uri = os.getenv("MONGO_URL")

# --- 2. Components ---
model = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview", 
    google_api_key=google_api_key,
    temperature=0
)

mongo_client = MongoClient(mongo_uri)
memory = MongoDBSaver(mongo_client)

# Use a per-process unique thread_id unless explicitly overridden.
# This avoids reusing old, incompatible checkpoints that cause "memory conflict" errors.
THREAD_ID = os.getenv("THREAD_ID") or f"finance_session_{uuid.uuid4()}"

mcp_client = MultiServerMCPClient({
    "mongo_mcp": {
        "url": "http://127.0.0.1:8081/mcp",
        "transport": "streamable_http",
    },
})

# --- 3. Tool Filtering ---
def filter_tools_for_gemini(tools):
    for tool in tools:
        if hasattr(tool, "args_schema") and tool.args_schema:
            schema = tool.args_schema
            if not isinstance(schema, dict):
                try: schema = schema.schema()
                except AttributeError: schema = schema.model_json_schema()
            
            def clean_schema(d):
                if isinstance(d, dict):
                    d.pop("additionalProperties", None)
                    d.pop("$schema", None)
                    for v in d.values(): clean_schema(v)
            clean_schema(schema)
    return tools

# --- 4. Chat Logic ---
async def chat_function(message: str, history: list):
    try:
        raw_tools = await mcp_client.get_tools()
        tools = filter_tools_for_gemini(raw_tools)
        
        system_instruction = (
            "You are a Financial AI Copilot.\n"
            "- When you need data, use the 'find' tool.\n"
            "- The 'filter' argument MUST be a JSON object, not a string. "
            "  Correct: filter: {\"stock_cap\": \"large\"}. "
            "  Incorrect: filter: \"{'stock_cap': 'large'}\".\n"
            "- If you do not want to filter, pass an empty object: filter: {}.\n"
            "- Do NOT set the 'sort' argument at all. Omit 'sort' from the "
            "tool arguments; never pass a string such as 'asc' or 'desc' for 'sort'.\n"
        )

        # Use a stable thread_id for this running process (or env override)
        config = {"configurable": {"thread_id": THREAD_ID}}
        
        agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_instruction,
            checkpointer=memory,
        )

        # Using a streamlined invocation
        inputs = {"messages": [("user", message)]}
        result = await agent.ainvoke(inputs, config=config)
        
        return result["messages"][-1].content

    except Exception as e:
        # If the history is still stuck, this helps identify it
        if "ToolMessage" in str(e):
            return "⚠️ Memory conflict detected. Try typing 'reset' or change the thread_id."
        return f"❌ Error: {e}"

# --- 5. UI ---
iface = gr.ChatInterface(
    fn=chat_function,
    title="Financial AI Copilot (The Recovery Edition)",
    description="Memory cleared and optimized for tool-calling.",
)

if __name__ == "__main__":
    iface.launch(server_name="127.0.0.1", server_port=7860)