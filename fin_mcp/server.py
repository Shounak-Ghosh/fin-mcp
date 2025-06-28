# fin_mcp/server.py
from fastmcp import FastMCP
from .tools.sec_tools import get_cik, get_accession_numbers, parse_10k, lookup_ticker
from .tools.agent_tools import analyze_10k

mcp = FastMCP("FinMCP Server", version="1.0.0")

@mcp.tool
def fetch_10k_analysis(ticker: str, year: int | None = None) -> dict:
    """
    Fetch the 10-K analysis for a given ticker symbol and optional year.
    """
    return analyze_10k(ticker, year)

@mcp.tool
def fetch_ticker(company_name: str) -> str | None:
    """
    Fetch the ticker symbol for a given company name.
    """
    ticker = lookup_ticker(company_name)
    return {"ticker": ticker} if ticker else {"ticker": None}

@mcp.tool
def fetch_cik(ticker: str) -> str:
    return get_cik(ticker)

@mcp.tool
def fetch_accession_numbers(cik: str) -> dict:
    return get_accession_numbers(cik)

@mcp.tool
def fetch_10k_sections(accession_number: str, cik: str) -> dict:
    return parse_10k(accession_number, cik)

if __name__ == "__main__":
    mcp.run(transport="http")