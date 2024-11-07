from pymongo import MongoClient
from langchain_core.documents.base import Document
from src.model.singleton.singleton import Singleton

class MongoHandler(MongoClient, metaclass=Singleton):
    def __init__(self, host='localhost', port=27017):
        super().__init__(host, port)
        self.dbs = {self[key] for key in self.list_database_names()}
        self._main_db = None
        self._main_collection = None

    def get_collections_from_database(self, db_name):
        db = self[db_name]
        return db.list_collection_names()
    
    def get_collection(self, db_name, collection_name):
        db = self[db_name]
        if collection_name in db.list_collection_names():
            return db[collection_name]  
        else: 
            raise ValueError(f"Collection {collection_name} not found in database {db_name}")
        
    
    def set_main_db(self, db_name):
        if db_name in self.list_database_names():
            self._main_db = self[db_name]
        else:
            raise ValueError(f"Database {db_name} not found")
    
    def set_main_collection(self, collection_name):
        if collection_name in self._main_db.list_collection_names():
            self._main_collection = self._main_db[collection_name]
        else:
            self._main_collection = self._main_db[collection_name]
            print(f"WARNING: Collection {collection_name} not found in database {self._main_db.name}. Be aware that the collection is now being created.")
        
    def push_to_main_collection(self, data):
        if self._main_collection is not None:
            self._main_collection.insert_many(data)  
        else:
            raise ValueError(f"Main collection undefined, set it first")
        print(f"All documents pushed to collection '{self._main_collection.name}' in database '{self._main_db.name}'")

    def retrieve_documents_from_main_collection(self):
        if self._main_collection is not None:
            retrieved_docs = []
            for chunk in self._main_collection.find():
                doc = Document(page_content=chunk.get("page_content"), 
                        metadata=chunk.get("metadata"),
                        type='Document',
                        id=chunk.get("_id"))
                retrieved_docs.append(doc)
            return retrieved_docs
        else:
            raise ValueError(f"Main collection undefined, set it first")
        # retrieved_docs = []
        # for chunk in collection.find():
        #     doc = Document(page_content=chunk.get("page_content"), 
        #             metadata=chunk.get("metadata"),
        #             type='Document',
        #             id=chunk.get("_id"))
        #     retrieved_docs.append(doc)
        # return retrieved_docs