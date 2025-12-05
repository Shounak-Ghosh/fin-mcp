
try:
    from langchain_core.tools import Tool, StructuredTool
    print("Tool and StructuredTool found in langchain_core.tools")
except ImportError:
    print("Tool and StructuredTool NOT found in langchain_core.tools")
