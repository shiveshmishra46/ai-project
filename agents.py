## Importing libraries and files
import os
from dotenv import load_dotenv

load_dotenv()

from crewai import Agent, LLM
from tools import FinancialDocumentTool

# Initialize LLM (uses OpenAI by default)
# Set OPENAI_API_KEY and optionally OPENAI_MODEL in your .env
llm = LLM(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    api_key=os.getenv("OPENAI_API_KEY")
)

# Senior Financial Analyst Agent (professional and compliant)
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal=(
        "Provide a factual, document-grounded analysis for the user's query: {query}. "
        "Use only information supported by the provided financial PDF. If information is missing, state that explicitly."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "You are an experienced financial analyst skilled at interpreting corporate financial statements, "
        "summarizing key metrics, and explaining implications clearly and conservatively. "
        "You avoid speculation and clearly distinguish facts from assumptions."
    ),
    tools=[FinancialDocumentTool.read_data_tool],
    llm=llm,
    max_iter=5,
    max_rpm=30,
    allow_delegation=False
)

# Document verifier agent (optional; kept professional if used later)
verifier = Agent(
    role="Financial Document Verifier",
    goal=(
        "Determine whether the provided file appears to be a financial document and summarize the key contents, "
        "being explicit about any uncertainty."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "A meticulous reviewer who scans documents for financial context, ensuring conclusions are supported by text."
    ),
    tools=[FinancialDocumentTool.read_data_tool],
    llm=llm,
    max_iter=3,
    max_rpm=30,
    allow_delegation=False
)

# Example additional agents (not used in the primary flow, retained for future expansion)
investment_advisor = Agent(
    role="Investment Insights Specialist",
    goal=(
        "Provide cautious, diversified, and document-grounded investment insights. "
        "Avoid personalized financial advice; highlight trade-offs and uncertainties."
    ),
    verbose=True,
    backstory=(
        "You summarize potential implications and options based on the document while staying within informational scope."
    ),
    llm=llm,
    max_iter=4,
    max_rpm=30,
    allow_delegation=False
)

risk_assessor = Agent(
    role="Risk Assessment Specialist",
    goal=(
        "Identify material risks mentioned or implied by the document, clearly distinguishing facts, assumptions, and uncertainties."
    ),
    verbose=True,
    backstory=(
        "You produce balanced risk assessments supported by document evidence."
    ),
    llm=llm,
    max_iter=4,
    max_rpm=30,
    allow_delegation=False
)