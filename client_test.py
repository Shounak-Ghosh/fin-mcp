# client_test.py
import asyncio
import json
from fastmcp import Client
from fin_mcp.server import mcp

client = Client(mcp)

def extract_text_content(response):
    """Extract text content from MCP response"""
    if isinstance(response, list) and len(response) > 0:
        if hasattr(response[0], 'text'):
            text = response[0].text
        elif isinstance(response[0], dict) and 'text' in response[0]:
            text = response[0]['text']
        else:
            return response
        
        # Try to parse as JSON if it looks like a JSON string
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return text
    return response

async def test():
    async with client:
        cik_response = await client.call_tool("fetch_cik", {"ticker": "AAPL"})
        cik = extract_text_content(cik_response)
        print("CIK:", cik)

        acc_response = await client.call_tool("fetch_accession_numbers", {"cik": cik})
        acc = extract_text_content(acc_response)
        print("Accessions type:", type(acc))
        print("Accessions:", acc)
        
        if isinstance(acc, dict):
            print("First few years:", list(acc.keys())[:3])
            acc_num = list(acc.values())[0]
            
            sections_response = await client.call_tool("fetch_10k_sections", {
                "accession_number": acc_num,
                "cik": cik
            })
            sections = extract_text_content(sections_response)
            print("Section 1A Snippet:", sections.get("item_1a", "")[:300])
        else:
            print("Unexpected response format for accessions")

asyncio.run(test())