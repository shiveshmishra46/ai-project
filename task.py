## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier
from tools import FinancialDocumentTool

## Primary task: grounded analysis of the provided financial PDF
analyze_financial_document = Task(
    description=(
        "Read the provided financial PDF using the tool read_data_tool(path='data/sample.pdf'). "
        "Then provide a concise, document-grounded analysis addressing the user's query: {query}. "
        "Focus on factual content explicitly supported by the document. "
        "If data is missing or unclear, state that explicitly and avoid speculation."
    ),
    expected_output="""A structured response with:
- Executive Summary (2-4 bullet points)
- Key Financial Highlights (revenue, margins, cash flow, guidance if present; cite where in the doc)
- Notable Risks and Assumptions (clearly mark assumptions)
- Implications (non-prescriptive, informational)
- Data Sources (which document sections/pages informed the analysis)
""",
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

## Additional optional tasks (not used by the core flow)
investment_analysis = Task(
    description=(
        "Based strictly on the document text (via read_data_tool), extract relevant financial details "
        "and outline neutral, informational investment considerations without giving personalized advice."
    ),
    expected_output="""An outline of:
- Extracted evidence (quotes/metrics from the document)
- Potential considerations (pros/cons, uncertainties)
- Gaps or missing information
- Data sources
""",
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

risk_assessment = Task(
    description=(
        "Using only the document text (via read_data_tool), identify material risks, citing where they appear, "
        "and provide a balanced summary. Avoid speculation."
    ),
    expected_output="""Risk summary including:
- Document-cited risks (with references)
- Potential impact (if stated)
- Unknowns/uncertainties
- Data sources
""",
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)