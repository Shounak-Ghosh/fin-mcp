# fin_mcp/agents/supervisor_agent.py
from langchain_core.prompts import PromptTemplate
from .base_agent import BaseAgent
from fin_mcp.models.state import GraphState

SUPERVISOR_PROMPT = """
 You are a senior analyst preparing a summary for an investor.
Based on the extracted risks and tone analysis, generate:
A short risk report for the company


Any contradictions between the tone and risks

Input:
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
        result = chain.invoke({"top_risks": state.top_risks, "tone_summary": state.tone_summary})
        return {"summary": result.content.strip()}