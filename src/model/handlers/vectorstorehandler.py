from langchain_community.vectorstores import FAISS
from src.model.singleton.singleton import Singleton

class VectorStoreHandler(metaclass=Singleton):
    def __init__(self, embeddings_model, documents=None):
        self.embeddings_model = embeddings_model
        self.documents = documents if documents is not None else []
        self._create_vectorstore() if documents is not None else None

    def _create_vectorstore(self):
            self.vectorstore = FAISS.from_documents(self.documents, self.embeddings_model)
    
    def add_documents(self, new_documents, replace=False):
        ids = [doc.id for doc in self.documents]
        if any(doc.id in ids for doc in new_documents) and not replace:
            raise ValueError("Document IDs must be unique. If you wish to update a document, specify the 'replace' parameter.")
        elif any(doc.id in ids for doc in new_documents) and replace:
            print("FUNCTIONALITY NOT IMPLEMENTED YET")
        else:
            self._update_vectorstore(new_documents)
            self.documents.extend(new_documents)

    def _update_vectorstore(self, new_documents):
        self.vectorstore.add_documents(new_documents, embeddings_model=self.embeddings_model)

    def total_documents(self):
        return self.vectorstore.index.ntotal

    def similarity_search(self, query, k=5):
        if self.vectorstore is None:
            raise ValueError("Vector store is empty. Add documents before searching.")
        return self.vectorstore.similarity_search(query, k=k)
    
    def as_retriever(self):
        return self.vectorstore.as_retriever()
