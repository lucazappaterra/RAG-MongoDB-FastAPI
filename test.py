from src.model import handlers
from langchain_community.embeddings import HuggingFaceBgeEmbeddings


db_handler = handlers.MongoHandler()

db_handler.set_main_db('papers')
db_handler.set_main_collection('papers_collection_proj')

docs = db_handler.retrieve_documents_from_main_collection()

embeddings_model = HuggingFaceBgeEmbeddings(
                model_name="BAAI/bge-small-en-v1.5",  # alternatively use "sentence-transformers/all-MiniLM-l6-v2" (faster)
                model_kwargs={'device':'cpu'}, #CPU run or 'device': 'cuda' for GPU use
                encode_kwargs={'normalize_embeddings': True} #Normalization is active, which means that the resulting vectors will have unit length. Normalization can be useful when you want to compare the similarity of sentences using methods like dot product or cosine similarity, as it makes the embeddings comparable on a common scale.
                )
vector_store = handlers.VectorStoreHandler(embeddings_model=embeddings_model, documents=docs)
retriever = vector_store.as_retriever()

similar_docs = retriever.invoke("What is BERT?", k=3)

print(similar_docs[0].id)