# Arquivo: agente/rag.py
import os
import shutil
import pandas as pd
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Variáveis globais para Cache (Singleton)
_cached_embeddings = None
_cached_vectorstore = None

PERSIST_DIRECTORY = "./chroma_db"

def get_embeddings_model():
    """
    Retorna o modelo de embeddings (Singleton).
    Carrega na memória apenas na primeira vez.
    """
    global _cached_embeddings
    if _cached_embeddings is None:
        print("⚡ Carregando modelo de embeddings (Isso acontece apenas uma vez)...")
        _cached_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _cached_embeddings

def ingest_data():
    """
    Lê o CSV e recria o banco ChromaDB.
    """
    print("🔄 Iniciando ingestão de dados...")
    
    if os.path.exists(PERSIST_DIRECTORY):
        shutil.rmtree(PERSIST_DIRECTORY)
        print("🗑️ Banco antigo removido.")

    # Ajuste o caminho conforme necessário
    csv_path = "data/base_conhecimento_ifood_genai_exemplo.csv" 
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo {csv_path} não encontrado.")
        return

    documents = []
    for _, row in df.iterrows():
        # Tratamento simples para garantir string
        content = f"Pergunta: {row['pergunta']}\nResposta: {row['resposta']}\nFonte: {row['fonte']}"
        metadata = {"categoria": str(row["categoria"]), "fonte": str(row["fonte"])}
        documents.append(Document(page_content=content, metadata=metadata))

    # Cria e persiste
    global _cached_vectorstore
    _cached_vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=get_embeddings_model(), 
        persist_directory=PERSIST_DIRECTORY
    )
    
    print(f"✅ Sucesso! {len(documents)} itens indexados.")
    return _cached_vectorstore

def get_retriever():
    """
    Retorna o retriever usando a conexão já aberta ou abre uma nova.
    """
    global _cached_vectorstore
    
    if _cached_vectorstore is None:
        _cached_vectorstore = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=get_embeddings_model()
        )
        
    return _cached_vectorstore.as_retriever(search_kwargs={"k": 3})

if __name__ == "__main__":
    ingest_data()