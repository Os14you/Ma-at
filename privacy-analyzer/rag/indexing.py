import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def build_index():

    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_path, "data")
    persist_dir = os.path.join(base_path, "chroma_db")

    print(f"Loading documents from {data_dir}...")
    loader = DirectoryLoader(data_dir, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()

    print("Chunking text...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    

    for chunk in chunks:
        filename = os.path.basename(chunk.metadata['source'])
        chunk.metadata['company'] = filename.replace('.md', '')

    print("Embedding and storing in ChromaDB...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=persist_dir
    )
    print(f"Successfully indexed {len(chunks)} chunks into ChromaDB at {persist_dir}.")

if __name__ == "__main__":
    build_index()
