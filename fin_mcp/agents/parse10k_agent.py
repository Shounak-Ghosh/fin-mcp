# agents/parse10k_agent.py
from .base_agent import BaseAgent
from fin_mcp.tools.sec_tools import get_cik, get_accession_numbers, parse_10k
from fin_mcp.models.state import GraphState
from fin_mcp.tools.sec_tools import get_cik, get_accession_numbers, parse_10k

class Parse10KAgent(BaseAgent):
    def __init__(self, llm):
        super().init(llm)

    def run(self, state: GraphState) -> dict:
        ticker = state.ticker  # assume input is a Pydantic state object with .ticker
        year = getattr(state, 'year', None)  # optional year parameter

        # print(f"Running Parse10KAgent for ticker: {ticker}, year: {year}")  

        try:
            cik = get_cik(ticker)
            acc_map = get_accession_numbers(cik)
            if not acc_map:
                raise ValueError(f"No 10-Ks found for {ticker}")
            
            if year is None:
                # If no year is specified, choose the most recent year
                chosen_year = next(iter(acc_map))
            elif year in acc_map:
                chosen_year = year
            else:
                # Find the closest year available
                closest_year = min(acc_map.keys(), key=lambda y: abs(y - year))
                chosen_year = closest_year
            # print(f"Chosen year for {ticker}: {chosen_year}")  # Debugging line
            accession_number = acc_map[chosen_year]
            sections = parse_10k(accession_number, cik)
            
            return {
                "year": chosen_year,
                "risk_factors": sections.get("item_1a", ""),
                "mdna": sections.get("item_7", "") + "\n\n" + sections.get("item_7a", ""),
                "ticker": ticker,
            }
        except Exception as e:
            return {"error": str(e)}