import os
import yaml
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv


base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_path, ".env"))

def get_llm(temperature=0.3):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    base_url = os.environ.get("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
    model_name = os.environ.get("OPENROUTER_MODEL", "openrouter/owl-alpha")
    
    if not api_key:
        print("[DEBUG] OPENROUTER_API_KEY not found in env, falling back to default ChatOpenAI.")
        return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
        
    return ChatOpenAI(
        model=model_name,
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=temperature
    )

def get_retriever():
    persist_dir = os.path.join(base_path, "chroma_db")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    return vectorstore

def generate_hyde_query(user_query: str) -> str:
    """Generates a hypothetical legal clause based on the user question."""
    llm = get_llm(temperature=0.3)
    
    prompts_path = os.path.join(base_path, "prompts.yml")
    with open(prompts_path, "r", encoding="utf-8") as f:
        prompts = yaml.safe_load(f)
    
    hyde_prompt = PromptTemplate.from_template(prompts["hyde_prompt"])
    
    chain = hyde_prompt | llm
    hypothetical_document = chain.invoke({"question": user_query})
    return hypothetical_document.content

def get_matching_companies(query: str) -> list:
    query_lower = query.lower()
    
    company_files = {}
    data_dir = os.path.join(base_path, "data")
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith(".md"):
                company_id = filename[:-3]
                main_name = company_id.split(".")[0].lower()
                if main_name not in company_files:
                    company_files[main_name] = []
                if company_id not in company_files[main_name]:
                    company_files[main_name].append(company_id)
                    
    aliases = {
        "meta": ["facebook.com"],
        "apple": ["icloud.com"],
        "microsoft": ["outlook.com"],
        "hotmail": ["outlook.com"],
        "gmail": ["gmail.com", "google.com"],
    }
    
    matched = set()
    
    for alias, companies in aliases.items():
        if alias in query_lower:
            matched.update(companies)
            
    for main_name, companies in company_files.items():
        if main_name in query_lower:
            matched.update(companies)
        for company_id in companies:
            if company_id in query_lower:
                matched.add(company_id)
                
    return list(matched)

def search_documents(query: str, use_hyde: bool = True):
    vectorstore = get_retriever()
    search_query = generate_hyde_query(query) if use_hyde else query
    
    matching_companies = get_matching_companies(query)
    search_filter = None
    if matching_companies:
        search_filter = {"company": {"$in": matching_companies}}
        
    results = vectorstore.similarity_search(search_query, k=4, filter=search_filter)
    
    return [doc.page_content for doc in results]
