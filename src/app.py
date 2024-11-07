from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

from src.model import handlers
from src.model.chatbot.withhistory import ChatbotWithHistory
import uuid

USER_ID = uuid.uuid4()
CONVERSATION_ID = uuid.uuid4()

app = FastAPI()
# creare vector store
app.vector_store = None
app.db_handler = handlers.MongoHandler() 
app.chatbot = ChatbotWithHistory()

print("Loading embedding model...")
try:
    app.embeddings_model = HuggingFaceBgeEmbeddings(
                model_name="BAAI/bge-small-en-v1.5",  # alternatively use "sentence-transformers/all-MiniLM-l6-v2" (faster)
                model_kwargs={'device':'cpu'}, #CPU run or 'device': 'cuda' for GPU use
                encode_kwargs={'normalize_embeddings': True} #Normalization is active, which means that the resulting vectors will have unit length. Normalization can be useful when you want to compare the similarity of sentences using methods like dot product or cosine similarity, as it makes the embeddings comparable on a common scale.
                )
except Exception as e:
    print(f"Run into exception {e}, are you connected to the VPN?")

# riempire nell'ingestion
# richiamare nell'ask

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/list_{db_name}")
async def get_collections(db_name: str) -> List[str]:
    app.db_handler.set_main_db(db_name)
    collections = app.db_handler.get_collections_from_database(db_name)
    return collections

@app.get("/ingestion") # per ora è una get perché i file li carico dalla cartella
async def insert_pdf(): # incorporare il nome del db e della collection come parametri
    db_name = "papers" 
    collection_name = "papers_collection_proj"
    pdfs_path = "./src/files_pdf/"

    app.db_handler.set_main_db(db_name)
    app.db_handler.set_main_collection(collection_name)
    processor = handlers.PDFHandler(pdfs_path, verbose=True)
    dicts_after_split = processor.load_and_split(return_dicts=True)

    if collection_name not in app.db_handler.get_collections_from_database(db_name):
        app.db_handler.push_to_main_collection(dicts_after_split)
    else:
        retrieved_docs = app.db_handler.retrieve_documents_from_main_collection() 
        if len(retrieved_docs) == len(dicts_after_split):
            print("Files already exists in the db, skipping ingestion")
        else:
            print("Update function not implemented yet")# probabilmente la creazione del db andrebbe fatta separatamente

    app.vector_store = handlers.VectorStoreHandler(embeddings_model=app.embeddings_model, documents=retrieved_docs)
    return f"All files are loaded in '{db_name}' database and the vector store is now ready to be queried"

@app.post("/query_vs/{query}")
async def query_vs(query: str = "What is BERT?") -> Dict:
    if app.vector_store is None:
        raise ValueError("Vector store is not ready yet. Please load the documents first")
    else:
        result = app.vector_store.similarity_search(query, k=3)
        result = {doc_num: doc for doc_num, doc in enumerate(result)}
    return result
    

@app.post("/ask_question")
async def ask_question(question: str):
    if app.vector_store is None:
        raise ValueError("Vector store is not ready yet. Please load the documents first")
    else:
        retriever = app.vector_store.as_retriever()
        app.chatbot.create_chain_with_history(retriever) 
        answer = app.chatbot.ask_question(question)
    return answer