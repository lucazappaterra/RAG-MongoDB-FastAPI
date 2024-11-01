from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

from model import handlers
from model.chatbot.withhistory import ChatbotWithHistory

app = FastAPI()
# creare vector store
app.vector_store = None
app.db_handler = handlers.MongoHandler() 


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

@app.get("/list_{db_name}")
async def get_collections(db_name: str) -> List[str]:
    app.db_handler.set_main_db(db_name)
    collections = app.db_handler.get_collections_from_database(db_name)
    return collections

@app.get("/ingestion") # per ora è una get perché i file li carico dalla cartella
async def insert_pdf(): # incorporare il nome del db e della collection come parametri
    app.db_handler.set_main_db('papers')
    app.db_handler.set_main_collection('papers_collection_proj')
    
    processor = handlers.PDFHandler("./files_pdf/", verbose=True)
    dicts_after_split = processor.load_and_split(return_dicts=True)
    app.db_handler.push_to_main_collection(dicts_after_split)

    retrieved_docs = app.db_handler.retrieve_documents_from_main_collection() # probabilmente la creazione del db andrebbe fatta separatamente
    app.vector_store = handlers.VectorStoreHandler(embeddings_model=app.embeddings_model, documents=retrieved_docs)
    return "All files are loaded in the db and the vector store is now ready to be queried"

@app.get("/query_vs/{query}")
async def query_vs(query: str = "What is BERT?") -> Dict:
    result = app.vector_store.similarity_search(query, k=3)
    return result
    

@app.post("/ask_question")
async def ask_question(question: str):
    return {"question": question}