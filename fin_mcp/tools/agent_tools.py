# fin_mcp/tools/agent_tools.py
from typing import Optional
from fin_mcp.graph.langgraph_builder import graph
from fin_mcp.models.state import GraphState

def as_graph_state(output_dict: dict) -> GraphState:
    return GraphState.model_validate(output_dict)

# Runs the LangGraph to analyze a company's 10-K report
# Takes a ticker symbol and an optional year, returns a formatted string with the analysis results
def analyze_10k(ticker: str, year: Optional[int] = None) -> dict:
    state = GraphState(ticker=ticker, year=year)
    result_dict = graph.invoke(state)
    # print("FINAL STATE:", result_dict)
    result = as_graph_state(result_dict)
    
    if result.error:
        return f"❌ Error: {result.error}"
    
    return {
    "top_risks": result.top_risks.strip(),
    "tone_summary": result.tone_summary.strip(),
    "summary": result.summary.strip()
}
