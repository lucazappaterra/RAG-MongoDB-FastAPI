from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

from src.model import handlers
from src.logger.logger import logger
from src.model.chatbot.withhistory import ChatbotWithHistory
from datetime import datetime
import uuid

class QuestionPayload(BaseModel):
    user_id: str
    question: str
    conversation_id: str = None

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
    logger.info("Root endpoint called")
    return {"message": "Hello World"}

@app.get("/list_{db_name}")
async def get_collections(db_name: str) -> List[str]:
    logger.info(f"Getting collections for database: {db_name}")
    app.db_handler.set_main_db(db_name)
    collections = app.db_handler.get_collections_from_database(db_name)
    logger.info(f"Collections retrieved: {collections}")
    return collections

@app.get("/ingestion") # per ora è una get perché i file li carico dalla cartella
async def insert_pdf(): # incorporare il nome del db e della collection come parametri
    db_name = "papers" 
    collection_name = "papers_collection_proj"
    pdfs_path = "./src/files_pdf/"

    logger.info(f"Starting ingestion for database: {db_name}, collection: {collection_name}")
    app.db_handler.set_main_db(db_name)
    app.db_handler.set_main_collection(collection_name)
    processor = handlers.PDFHandler(pdfs_path, verbose=True)
    dicts_after_split = processor.load_and_split(return_dicts=True)

    if collection_name not in app.db_handler.get_collections_from_database(db_name):
        app.db_handler.push_to_main_collection(dicts_after_split)
        logger.info("Documents pushed to the collection")
    else:
        retrieved_docs = app.db_handler.retrieve_documents_from_main_collection() 
        if len(retrieved_docs) == len(dicts_after_split):
            logger.info("Files already exist in the db, skipping ingestion")
        else:
            logger.warning("Update function not implemented yet")# probabilmente la creazione del db andrebbe fatta separatamente

    app.vector_store = handlers.VectorStoreHandler(embeddings_model=app.embeddings_model, documents=retrieved_docs)
    logger.info("Vector store is now ready to be queried")
    return f"All files are loaded in '{db_name}' database and the vector store is now ready to be queried"

@app.post("/query_vs/{query}")
async def query_vs(query: str = "What is BERT?") -> Dict:
    logger.info(f"Querying vector store with query: {query}")
    if app.vector_store is None:
        logger.error("Vector store is not ready yet. Please load the documents first")
        raise ValueError("Vector store is not ready yet. Please load the documents first")
    else:
        result = app.vector_store.similarity_search(query, k=3)
        result = {doc_num: doc for doc_num, doc in enumerate(result)}
        logger.info(f"Query results: {result}")
    return result
    
@app.post("/ask_question")
async def ask_question(payload: QuestionPayload) -> Dict:
    logger.info(f"Received question from user: {payload.user_id}, question: {payload.question}")
    if app.vector_store is None:
        logger.error("Vector store is not ready yet. Please load the documents first")
        raise ValueError("Vector store is not ready yet. Please load the documents first")
    else:
        if payload.conversation_id is None:
            payload.conversation_id = str(uuid.uuid4())
            logger.info(f"Generated new conversation ID: {payload.conversation_id}")

        retriever = app.vector_store.as_retriever()
        app.chatbot.create_chain_with_history(retriever) 
        response = app.chatbot.ask_question(payload.question)
        db_payload = {
            "user_id": payload.user_id, 
            "conversation_id": payload.conversation_id, 
            "question": payload.question,
            "answer": response.get("output").content,
            "context": response.get("context"),
            "timestamp": datetime.now().isoformat()
            # "history": response["history"]
        }
        app.db_handler.save_conversation_history(db_payload)

    return {
        "user_id": payload.user_id, 
        "conversation_id": payload.conversation_id, 
        "response": response
    }