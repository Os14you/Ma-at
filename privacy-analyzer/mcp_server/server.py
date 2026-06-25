from fastmcp import FastMCP
from datetime import datetime, timedelta

mcp = FastMCP("PrivacyLegalServer")

@mcp.tool()
def calculate_data_retention(deletion_date_str: str, retention_period_days: int) -> str:
    """
    Calculates the exact date user data will be purged.
    
    Args:
        deletion_date_str: The date the account was deleted in YYYY-MM-DD format.
        retention_period_days: Number of days the company holds the data.
    """
    try:
        deletion_date = datetime.strptime(deletion_date_str, "%Y-%m-%d")
        purge_date = deletion_date + timedelta(days=retention_period_days)
        return f"Data will be permanently purged on: {purge_date.strftime('%Y-%m-%d')}"
    except ValueError:
        return "Error: deletion_date_str must be in YYYY-MM-DD format."

@mcp.tool()
def define_legal_term(term: str) -> str:
    """
    Looks up dense legal jargon and returns a simple definition.
    
    Args:
        term: The legal term to define (e.g., 'arbitration', 'third-party', 'indemnification', 'force majeure').
    """
    dictionary = {
        "arbitration": "A private dispute resolution process where a neutral third party makes a binding decision, preventing you from suing the company in normal court.",
        "third-party": "An entity not directly involved in the agreement (e.g., advertisers, analytics companies).",
        "indemnification": "A clause requiring you to pay for the company's legal costs if your actions cause them to be sued.",
        "force majeure": "Unforeseeable circumstances that prevent someone from fulfilling a contract (like natural disasters)."
    }
    term_lower = term.lower()
    for key, definition in dictionary.items():
        if key in term_lower:
            return f"Definition of {key.title()}: {definition}"
    return f"Term '{term}' not found in the legal dictionary."

@mcp.resource("legal://user-rights/ccpa")
def get_ccpa_rights() -> str:
    """Returns static context about the California Consumer Privacy Act (CCPA)."""
    return """
    CCPA Core Rights:
    1. Right to Know: Consumers can request details on what personal data is collected.
    2. Right to Delete: Consumers can request deletion of personal data.
    3. Right to Opt-Out: Consumers can stop the sale of their personal data.
    4. Right to Non-Discrimination: Equal service and price even if privacy rights are exercised.
    """

if __name__ == "__main__":
    mcp.run()
