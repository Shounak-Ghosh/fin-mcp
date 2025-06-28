# fin_mcp/server.py
from fastmcp import FastMCP
from .sec_tools import get_cik, get_accession_numbers, parse_10k

mcp = FastMCP("SEC API MCP Server", version="1.0.0")

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
    mcp.run()