# chat_demo/chat_agent.py
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool, StructuredTool
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage, AIMessageChunk
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from fastmcp import Client
import asyncio
import json

from dotenv import load_dotenv
load_dotenv(override=True) 

from typing import Dict, AsyncIterator, Optional
from pydantic import BaseModel

class _Analyze10KInput(BaseModel):
    ticker: str
    year: Optional[int] = None


mcp_client = Client("http://127.0.0.1:8000/mcp")

async def call_mcp_tool(tool_name: str, args: dict):
    async with mcp_client:
        result = await mcp_client.call_tool(tool_name, args)
        if isinstance(result, list) and hasattr(result[0], "text"):
            try:
                return json.loads(result[0].text)
            except Exception:
                return result[0].text
        return result


# Define tools (keep as is)
tools = [
    StructuredTool.from_function(
        name="Analyze10K",
        func= lambda ticker, year=None: asyncio.run(call_mcp_tool("fetch_10k_analysis", {"ticker": ticker, "year": year})),
        description=(
            "Use this tool to analyze a company's 10-K report. "
            "Input must be a dictionary with 'ticker' (e.g. 'AAPL' or 'MSFT') and optionally 'year' (e.g. 2022). "
            "Returns top risks, tone summary, and a high-level summary."
        ),
        args_schema=_Analyze10KInput,
    ),
    Tool(
        name="LookupTicker",
        func= lambda name: asyncio.run(call_mcp_tool("fetch_ticker", {"company_name": name}))["ticker"],
        description="Use this tool to look up the stock ticker for a given company name. Input should be the formal company name (e.g. Apple Inc. or Alphabet). The output will be the stock ticker symbol (e.g. AAPL or GOOGL). If no ticker is found, the output will be None.",
    ),
]

# Define the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True) # Ensure streaming is enabled

# Define the system prompt
system_prompt = """
You are a financial assistant. When users mention company names like 'Apple' or 'Google',
always convert them to stock tickers like 'AAPL' or 'GOOGL' before passing to tools.
Use the LookupTicker tool if needed. When calling the Analyze10K tool, you will receive structured data including 'top_risks', 'tone_summary', and 'summary'.
Use that data to write a detailed, well-phrased explanation to the user. 
Always refer to the conversation history to see if you can answer questions without additional tool calling -- the user may have already asked for analysis for a given ticker, year 10-K report.  
Only call one tool at a time and wait for its response before proceeding. 
Do not call multiple tools in parallel or try to aggregate results from multiple tools in a single response.
If you feel multiple tools are needed, call them sequentially (ie wait for tool completion and response) and use the results to inform your final response.
"""

# Define the agent using langgraph
smart_chat_agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=system_prompt
)

async def stream_chat_agent(inputs: dict) -> AsyncIterator[Dict[str, str]]:
    user_input = inputs.get("input", "")
    chat_history_raw = inputs.get("chat_history", [])

    lc_messages = []
    for m in chat_history_raw:
        if isinstance(m, dict):
            role = m.get("role")
            content = m.get("content")
            if role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
        elif isinstance(m, BaseMessage):
            lc_messages.append(m)
    
    # Add the current user message
    lc_messages.append(HumanMessage(content=user_input))

    full_response_content = ""
    try:
        # Use astream_events for detailed streaming
        async for event in smart_chat_agent.astream_events(
            {"messages": lc_messages},
            version="v1"
        ):
            kind = event["event"]
            
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    full_response_content += content
                    yield {"output": full_response_content}
            
            # We can also handle tool calls if we want to show them, but for now just stream the final response
            # The react agent will yield tool calls and then the final response.
            # on_chat_model_stream will capture tokens from both tool calls and final response.
            # We might want to filter out tool call tokens if we only want the final answer, 
            # but usually showing the thought process is fine or we can filter based on event tags.
            # For simplicity, we stream everything the model says.
            
    except Exception as e:
        # Catch any unexpected errors from the agent's streaming process
        yield {"error": f"❌ Agent error: {str(e)}"}