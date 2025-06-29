# fin_mcp/agents/supervisor_agent.py
from langchain_core.prompts import PromptTemplate
from .base_agent import BaseAgent
from fin_mcp.models.state import GraphState

SUPERVISOR_PROMPT = """
You are a senior analyst preparing a summary for an investor.
Based on the extracted risks and tone analysis, generate the following:

A short risk report for the company

Any contradictions between the tone and risks

Make sure to include the year and ticker in the first sentence of your summary.

Input:
Year: 
{year}
Ticker:
    {ticker}
 Top Risks:
 {top_risks}
Tone Summary:
 {tone_summary}
 """

class SupervisorAgent(BaseAgent):
    def __init__(self, llm):
        super().init(llm)
        self.llm = llm

    def run(self, state: GraphState) -> dict:
        prompt = PromptTemplate.from_template(SUPERVISOR_PROMPT)
        chain = prompt | self.llm
        result = chain.invoke({"year": state.year,"ticker":state.ticker,"top_risks": state.top_risks, "tone_summary": state.tone_summary})
        return {"summary": result.content.strip()}