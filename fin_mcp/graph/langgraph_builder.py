# fin_mcp/graph/langgraph_builder.py
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.types import Send
from fin_mcp.models.state import GraphState
from fin_mcp.agents.risk_agent import RiskAgent
from fin_mcp.agents.tone_agent import ToneAgent
from fin_mcp.agents.supervisor_agent import SupervisorAgent
from fin_mcp.agents.parse10k_agent import Parse10KAgent
from langchain_openai import ChatOpenAI

load_dotenv()
load_dotenv(override=True)  # Force override
# print(os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

risk_agent = RiskAgent(llm=llm)
tone_agent = ToneAgent(llm=llm)
supervisor_agent = SupervisorAgent(llm=llm)
parse10k_agent = Parse10KAgent(llm)

def fanout_to_parallel_agents(state: GraphState):
    # Return list of parallel tasks
    return [
        Send("risk_agent", state),
        Send("tone_agent", state),
    ]

def build_langgraph():
    builder = StateGraph(GraphState)

    builder.add_node("parse10k_agent", parse10k_agent.run)
    builder.add_node("risk_agent", risk_agent.run)
    builder.add_node("tone_agent", tone_agent.run)
    builder.add_node("supervisor_agent", supervisor_agent.run)

    builder.set_entry_point("parse10k_agent")

    # Parallel fan-out using conditional edges
    builder.add_conditional_edges("parse10k_agent", fanout_to_parallel_agents, ["risk_agent", "tone_agent"])

    # Join both back into supervisor
    builder.add_edge("risk_agent", "supervisor_agent")
    builder.add_edge("tone_agent", "supervisor_agent")

    builder.add_edge("supervisor_agent", END)

    return builder.compile()

def visualize_graph(graph):
    # Paste the output into an Markdown file or a compatible editor
    mermaid_syntax = graph.get_graph().draw_mermaid()
    print("\n--- Mermaid Graph Syntax ---")
    print(mermaid_syntax)
    print("----------------------------")
    print("You can paste this into https://mermaid.live/ or a compatible editor.")

graph = build_langgraph()

# visualize_graph(graph)