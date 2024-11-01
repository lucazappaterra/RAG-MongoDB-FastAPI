from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

from model import handlers
from model.chatbot.withhistory import ChatbotWithHistory

app = FastAPI()
# creare vector store 
# riempire nell'ingestion
# richiamare nell'ask

@app.get("/collections")
async def get_collections():
    db_handler = handlers.MongoHandler()
    db_handler.set_main_db('papers')
    collections = db_handler.get_collections_from_database('papers')
    return collections

@app.get("/ingestion")
async def insert_pdf():
    db_handler = handlers.MongoHandler()
    db_handler.set_main_db('papers')
    db_handler.set_main_collection('papers_collection_test_bis')
    

@app.post("/ask_question")
async def ask_question(question: str):
    return {"question": question}