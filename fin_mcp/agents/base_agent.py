# fin_mcp/agents/base_agent.py
from abc import ABC, abstractmethod
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import Tool
# from langchain_core.runnables import Runnable

class BaseAgent(ABC):
    def __init__(self, llm: BaseLanguageModel, tools: list[Tool] = None):
        self.llm = llm
        self.tools = tools or []

    @abstractmethod
    def run(self, input: dict) -> dict:
        pass