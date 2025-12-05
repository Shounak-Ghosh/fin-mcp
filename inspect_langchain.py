
import langchain
import langchain.agents
print("langchain version:", langchain.__version__)
print("langchain.agents dir:", dir(langchain.agents))
try:
    from langchain.agents import AgentExecutor
    print("AgentExecutor found in langchain.agents")
except ImportError:
    print("AgentExecutor NOT found in langchain.agents")
