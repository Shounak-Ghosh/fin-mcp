# fin_mcp/graph/__init__.py
"""LangGraph workflow for multi-agent 10-K analysis."""

from .langgraph_builder import build_langgraph, graph

__all__ = ["build_langgraph", "graph"]
