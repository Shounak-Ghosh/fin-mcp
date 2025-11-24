# fin_mcp/agents/risk_agent.py
from langchain_core.prompts import PromptTemplate
from fin_mcp.models.state import GraphState
from .base_agent import BaseAgent

RISK_PROMPT = """
You are an expert financial analyst. Extract the top 3 strategic risks from the following Item 1A (Risk Factors) section of a 10-K filing.
Text:
 {risk_factors}
Return a numbered list of three risks with brief explanations.
"""

class RiskAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm)
        self.llm = llm

    def run(self, state: GraphState) -> dict:
        print(f"[RISK AGENT] Running for {state.ticker}")
        prompt = PromptTemplate.from_template(RISK_PROMPT)
        chain = prompt | self.llm

        # Convert Pydantic input to dict and extract what we need
        risk_text = state.risk_factors
        result = chain.invoke({"risk_factors": risk_text})
        print("[Risk Agent] DONE")
        return {"top_risks": result.content.strip()}