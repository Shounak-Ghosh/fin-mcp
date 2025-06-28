# chat_demo/chat_agent.py
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool, StructuredTool
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage, AIMessageChunk
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from fastmcp import Client
import asyncio
import json
import asyncio 

from dotenv import load_dotenv
load_dotenv(override=True) 

from typing import Iterator, Dict, Union, AsyncIterator, Optional
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

# Define the prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """
You are a financial assistant. When users mention company names like 'Apple' or 'Google',
always convert them to stock tickers like 'AAPL' or 'GOOGL' before passing to tools.
Use the LookupTicker tool if needed. When calling the Analyze10K tool, you will receive structured data including 'top_risks', 'tone_summary', and 'summary'.
Use that data to write a detailed, well-phrased explanation to the user. Multiple tools can be called in a single response, so you may need to combine results from multiple Analyze10K calls.
"""),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# Define the agent (core runnable logic)
agent_runnable_logic = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

# AgentExecutor instance
smart_chat_agent = AgentExecutor(
    agent=agent_runnable_logic,
    tools=tools,
    verbose=True, # Keep verbose for debugging
    handle_parsing_errors=True
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

    full_response_content = ""
    try:
        # Use astream_log for detailed streaming, including final output word by word
        async for chunk in smart_chat_agent.astream_log({
            "input": user_input,
            "chat_history": lc_messages
        }):
            # Each chunk is a "log patch"
            for op in chunk.ops:
                # Look for 'add' operations that contain message content
                if op["op"] == "add":
                    # Check if the path corresponds to a message, especially the final output
                    # The path for the final AI message content often looks like:
                    # /logs/Agent/final_output/output/content
                    # or /logs/Agent/final_output/messages/0/content
                    # or directly from the LLM stream within the agent
                    if isinstance(op["value"], AIMessageChunk):
                        delta = op["value"].content
                        if delta:
                            full_response_content += delta
                            yield {"output": full_response_content}
                    elif isinstance(op["value"], dict) and "content" in op["value"] and op["path"].endswith("/content"):
                        # This might catch the final aggregated content
                        delta = op["value"]["content"]
                        if delta:
                            full_response_content = delta # Replace with full content if it's a complete message
                            yield {"output": full_response_content}
                    elif op["path"].endswith("/output") and isinstance(op["value"], str):
                        # This can catch the final string output of the agent
                        full_response_content = op["value"]
                        yield {"output": full_response_content}
                    elif op["path"].endswith("/output") and isinstance(op["value"], AIMessage):
                        # This can catch the final AIMessage object
                        full_response_content = op["value"].content
                        yield {"output": full_response_content}

    except Exception as e:
        # Catch any unexpected errors from the agent's streaming process
        yield {"error": f"❌ Agent error: {str(e)}"}