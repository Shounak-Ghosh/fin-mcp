# fin-mcp

An MCP (Model Context Protocol) server for AI-powered analysis of SEC 10-K filings using multi-agent LangGraph workflows.

## Overview

**fin-mcp** scrapes SEC EDGAR 10-K reports and analyzes them using a fan-in, fan-out multi-agent system built with LangChain and LangGraph. The system extracts key insights including strategic risks, management tone/sentiment, and comprehensive financial summaries.

### Features

- 🔍 **SEC Data Scraping**: Automated retrieval of 10-K filings from the SEC EDGAR database
- 🤖 **Multi-Agent Analysis**: Parallel processing with specialized AI agents:
  - **Parse10K Agent**: Fetches and extracts key sections from 10-K filings
  - **Risk Agent**: Identifies top 3 strategic risks from risk factors
  - **Tone Agent**: Analyzes management tone and sentiment from MD&A
  - **Supervisor Agent**: Synthesizes insights into comprehensive reports
- 🔌 **MCP Server**: Exposes analysis tools via Model Context Protocol for LLM integration
- 💬 **Gradio Chat Demo**: Interactive chatbot UI for exploring 10-K documents

### Architecture

```
User Query → Parse10K Agent → [Risk Agent + Tone Agent (parallel)] → Supervisor Agent → Final Report
```

## Installation

### Prerequisites

- Python 3.11 or higher
- OpenAI API key
- SEC API key

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/fin-mcp.git
cd fin-mcp

uv venv # Create virtual environment, needs to be activated

uv sync # Pull in dependencies

# Install dependencies (using uv)
uv pip install -e .

# Or install with pip
pip install -e .

# Optional: Install demo dependencies
uv pip install -e ".[demo]"
# Or with pip
pip install -e ".[demo]"
```

### Environment Setup

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
SEC_API_KEY=your_sec_api_key_here
```

## Usage

### Running the MCP Server

Start the MCP server to expose 10-K analysis tools:

```bash
# Using the Python module
# Helpful tip: Run the MCP server in a standalone terminal/bash shell
python -m fin_mcp.server
```

The server will start on HTTP transport and expose the following MCP tools:
- `fetch_10k_analysis`: Analyze a 10-K filing for a given ticker and year
- `fetch_ticker`: Look up ticker symbol from company name
- `fetch_cik`: Get CIK number from ticker symbol
- `fetch_accession_numbers`: Retrieve available 10-K accession numbers
- `fetch_10k_sections`: Parse specific sections from a 10-K filing

### Running the Gradio Demo

Launch the interactive chat interface:

```bash
# Using Python module
# Helpful tip: Run the MCP server in a standalone terminal/bash shell
python -m chat_demo.gradio_ui
```

Then open your browser to the URL shown (typically `http://127.0.0.1:7860`).

### Example Queries

Try these queries in the Gradio demo:

- "Analyze Apple's 2023 10-K filing"
- "What are the main risks for TSLA in 2022?"
- "Compare the management tone between Microsoft's 2021 and 2023 filings"
- "Get me the risk factors for NVDA"

## Available MCP Tools

When connecting an MCP client to the fin-mcp server, you'll have access to:

1. **fetch_10k_analysis(ticker: str, year: int | None)** - Complete AI-powered analysis
2. **fetch_ticker(company_name: str)** - Convert company name to ticker symbol
3. **fetch_cik(ticker: str)** - Get SEC CIK identifier
4. **fetch_accession_numbers(cik: str)** - List available 10-K filings
5. **fetch_10k_sections(accession_number: str, cik: str)** - Extract specific document sections

## Project Structure

```
fin-mcp/
├── fin_mcp/
│   ├── agents/          # LangChain agent implementations
│   │   ├── base_agent.py
│   │   ├── parse10k_agent.py
│   │   ├── risk_agent.py
│   │   ├── tone_agent.py
│   │   └── supervisor_agent.py
│   ├── graph/           # LangGraph workflow builder
│   │   └── langgraph_builder.py
│   ├── models/          # Pydantic state models
│   │   └── state_models.py
│   ├── tools/           # SEC scraping and agent tools
│   │   ├── sec_tools.py
│   │   └── agent_tools.py
│   └── server.py        # FastMCP server
├── chat_demo/           # Gradio demo application
│   ├── chat_agent.py
│   └── gradio_ui.py
├── pyproject.toml       # Package configuration
└── README.md
```

## How It Works

1. **Data Collection**: The Parse10K agent fetches company 10-K filings from SEC EDGAR using ticker symbols
2. **Section Extraction**: Key sections are parsed from the HTML filing (Item 1A - Risk Factors, Item 7 - MD&A, Item 7A)
3. **Parallel Analysis**: Risk and Tone agents analyze their respective sections concurrently
4. **Synthesis**: The Supervisor agent combines insights into a comprehensive report
5. **Delivery**: Results are returned via MCP tools or the Gradio chat interface

## Requirements

- `beautifulsoup4>=4.12.0` - HTML parsing
- `fastmcp>=2.9.2` - MCP server framework
- `langchain>=0.3.26` - Agent framework
- `langchain-core>=0.3.0` - Core LangChain primitives
- `langchain-openai>=0.3.27` - OpenAI integration
- `langgraph>=0.5.0` - Multi-agent orchestration
- `lxml>=6.0.0` - XML/HTML parser
- `openai>=1.93.0` - OpenAI API client
- `pandas>=2.3.0` - Data processing
- `python-dotenv>=1.0.0` - Environment configuration
- `requests>=2.32.4` - HTTP requests
- `gradio>=5.35.0` - Chat demo UI (optional)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Acknowledgments

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [LangChain](https://www.langchain.com/) - Agent framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent workflows
- [Gradio](https://www.gradio.app/) - Demo interface