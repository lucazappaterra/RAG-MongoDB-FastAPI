import uvicorn
from fastapi import FastAPI
# from langchain_community.embeddings import HuggingFaceBgeEmbeddings

from src.app import app

# mainApp = FastAPI()
# mainApp.mount("/app", app)  # your app routes will now be /app/{your-route-here}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
