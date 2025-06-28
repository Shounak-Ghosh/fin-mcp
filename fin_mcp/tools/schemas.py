# fin_mcp/tools/schemas.py
from pydantic import BaseModel
from typing import Optional

class Analyze10KInput(BaseModel):
    ticker: str
    year: Optional[int] = None