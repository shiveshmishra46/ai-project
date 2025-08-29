## Importing libraries and files
import os
from dotenv import load_dotenv

load_dotenv()

from pypdf import PdfReader
from crewai_tools.tools.serper_dev_tool import SerperDevTool
from crewai_tools import tool

## Optional search tool (not used in the core flow; requires SERPER_API_KEY if used)
search_tool = SerperDevTool()

## Creating custom PDF reader tool
class FinancialDocumentTool:
    @staticmethod
    @tool("Read Financial PDF")
    def read_data_tool(path: str = "data/sample.pdf") -> str:
        """Reads a PDF file from 'path' and returns cleaned text.
        Args:
            path (str): Path to the PDF file. Defaults to 'data/sample.pdf'.
        Returns:
            str: Full document text with normalized whitespace.
        Raises:
            FileNotFoundError: If the file is not found.
            ValueError: If the file content could not be extracted.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"PDF not found at path: {path}")

        reader = PdfReader(path)
        pages_text = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

        full_report = "\n".join(pages_text)

        # Normalize whitespace and newlines
        while "\n\n" in full_report:
            full_report = full_report.replace("\n\n", "\n")
        # Collapse multiple spaces
        while "  " in full_report:
            full_report = full_report.replace("  ", " ")

        if not full_report.strip():
            raise ValueError("No extractable text found in the PDF.")

        return full_report


## Additional placeholders for future expansion (not wired to Crew)
class InvestmentTool:
    @staticmethod
    def analyze_investment_tool(financial_document_data: str) -> str:
        # Placeholder for future logic
        return "Investment analysis functionality to be implemented"


class RiskTool:
    @staticmethod
    def create_risk_assessment_tool(financial_document_data: str) -> str:
        # Placeholder for future logic
        return "Risk assessment functionality to be implemented"