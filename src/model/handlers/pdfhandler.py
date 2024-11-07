from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.model.singleton.singleton import Singleton

class PDFHandler(metaclass=Singleton):
    def __init__(self, directory, chunk_size=2000, chunk_overlap=200, verbose=False):
        self.directory = directory
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.verbose = verbose
        
        self.loader = PyPDFDirectoryLoader(self.directory)
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=[".", "\n\n"],
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        self.docs_before_split = None
        self.docs_after_split = None

    def load_and_split(self, return_dicts=False):
        self.docs_before_split = self.loader.load()
        self.docs_after_split = self.text_splitter.split_documents(self.docs_before_split)
        self.print_split_info() if self.verbose else None
        if return_dicts:
            dicts_after_split = self.get_docs_dicts()
            return dicts_after_split
        else:
            return self.docs_after_split

    def print_split_info(self):
        avg_doc_length = lambda docs: sum([len(doc.page_content) for doc in docs])//len(docs)
        avg_char_before_split = avg_doc_length(self.docs_before_split)
        avg_char_after_split = avg_doc_length(self.docs_after_split)

        print(f'Before split, there were {len(self.docs_before_split)} documents loaded, with average characters equal to {avg_char_before_split}.')
        print(f'After split, there were {len(self.docs_after_split)} documents (chunks), with average characters equal to {avg_char_after_split} (average chunk length).')

    def get_docs_dicts(self):
        if self.docs_after_split:
            dicts_after_split = [chunk.model_dump() for chunk in self.docs_after_split]
        else:
            raise ValueError("Documents have not been split yet. Call load_and_split() first.")
        return dicts_after_split

    def __getitem__(self, index):
        if self.docs_after_split:
            return self.docs_after_split[index]
        else:
            raise ValueError("Documents have not been split yet. Call load_and_split() first.")