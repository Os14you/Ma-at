import os
import sys
import yaml
from dotenv import load_dotenv
from jinja2 import Template
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.retrieval import search_documents, get_llm

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_path, ".env"))


@tool
def calculate_data_retention(deletion_date_str: str, retention_period_days: int) -> str:
    """Calculates the exact date user data will be purged.
    
    Args:
        deletion_date_str: The date the account was deleted in YYYY-MM-DD format.
        retention_period_days: Number of days the company holds the data.
    """
    from datetime import datetime, timedelta
    try:
        deletion_date = datetime.strptime(deletion_date_str, "%Y-%m-%d")
        purge_date = deletion_date + timedelta(days=retention_period_days)
        return f"Data will be permanently purged on: {purge_date.strftime('%Y-%m-%d')}"
    except ValueError:
        return "Error: deletion_date_str must be in YYYY-MM-DD format."

@tool
def define_legal_term(term: str) -> str:
    """Looks up dense legal jargon and returns a simple definition.
    
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

def get_ccpa_rights() -> str:
    """Returns static context about the California Consumer Privacy Act (CCPA)."""
    return """
    CCPA Core Rights:
    1. Right to Know: Consumers can request details on what personal data is collected.
    2. Right to Delete: Consumers can request deletion of personal data.
    3. Right to Opt-Out: Consumers can stop the sale of their personal data.
    4. Right to Non-Discrimination: Equal service and price even if privacy rights are exercised.
    """

prompts_path = os.path.join(base_path, "prompts.yml")
with open(prompts_path, "r", encoding="utf-8") as f:
    prompts = yaml.safe_load(f)

system_prompt_template = Template(prompts["system_prompt"])

def run_agent(query: str):
    print(f"\n{'='*50}\nUser Query: {query}\n{'='*50}")
    
    print("[Agent] Retrieving relevant documents via HyDE...")
    retrieved_docs = search_documents(query)
    
    ccpa_info = ""
    if "ccpa" in query.lower() or "california" in query.lower():
        print("[Agent] Fetching CCPA resource...")
        ccpa_info = get_ccpa_rights()

    system_prompt = system_prompt_template.render(
        context_chunks=retrieved_docs,
        ccpa_context=ccpa_info
    )
    
    llm = get_llm(temperature=0)
    tools = [calculate_data_retention, define_legal_term]
    llm_with_tools = llm.bind_tools(tools)
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ]

    for step in range(3):
        response = llm_with_tools.invoke(messages)
        
        if response.tool_calls:
            messages.append(response)
            
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                tool_id = tool_call['id']
                
                print(f"\n[Agent wants to use a tool] -> {tool_name}({tool_args})")
                
                if tool_name == "define_legal_term":
                    result = define_legal_term.invoke(tool_args)
                elif tool_name == "calculate_data_retention":
                    result = calculate_data_retention.invoke(tool_args)
                else:
                    result = f"Error: Tool {tool_name} not found."
                
                print(f"[Tool Execution] => {result}")
                
                messages.append(ToolMessage(content=str(result), tool_call_id=tool_id))
        else:

            print(f"\n[Final Answer]:\n{response.content}")
            break

if __name__ == "__main__":
    queries = [
        "What is the 'arbitration' clause for Discord?",
        "If I delete my TikTok today (2026-06-25), and they keep data for 30 days, what exact date is my data wiped?",
        "Under CCPA, do I have the right to stop them from selling my data?"
    ]
    
    for q in queries:
        run_agent(q)
