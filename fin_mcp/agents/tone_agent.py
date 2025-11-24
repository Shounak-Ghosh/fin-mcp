# fin_mcp/agents/tone_agent.py
from langchain_core.prompts import PromptTemplate
from .base_agent import BaseAgent
from fin_mcp.models.state import GraphState

TONE_PROMPT = """
 You are a financial sentiment analyst. Read the following Item 7 (Management's Discussion) section and summarize the overall tone of the company's statements.
Is the management optimistic, cautious, defensive, or contradictory? Provide a one-paragraph summary.
Text:
 {mdna}
 """

class ToneAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm)
        self.llm = llm

    def run(self, state: GraphState) -> dict:
        print(f"[TONE AGENT] Running for {state.ticker}")
        prompt = PromptTemplate.from_template(TONE_PROMPT)
        chain = prompt | self.llm
        result = chain.invoke({'mdna': state.mdna})
        print("[Tone Agent] DONE")
        return {"tone_summary": result.content.strip()}