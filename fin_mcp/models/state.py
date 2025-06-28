# fin_mcp/models/state.py
import operator
from pydantic import BaseModel
from typing import Optional, Annotated

class GraphState(BaseModel):
    ticker: str = ""
    year: Optional[int] = None
    risk_factors: str = ""
    mdna: str = ""
    top_risks: str = ""
    tone_summary: str = ""
    summary: str = ""
    error: str = ""
    status_log: Annotated[list[str], operator.add] = []