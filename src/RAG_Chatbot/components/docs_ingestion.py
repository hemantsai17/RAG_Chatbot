from src.RAG_Chatbot.constants import CONFIG_YAMLPATH , PARAMS_YAMLPATH
from src.RAG_Chatbot.utils.common import *
from src.RAG_Chatbot.entity import *
from sentence_transformers import SentenceTransformer
import torch
from langchain.vectorstores import FAISS
# from langchain.embeddings import SentenceTransformer
from langchain.document_loaders import DirectoryLoader , PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter , RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
import os
from src.RAG_Chatbot.logging import logger
import faiss
import pickle
import numpy as np
from langchain.docstore import InMemoryDocstore
import os
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore

from fastapi import UploadFile, File, HTTPException
from typing import List



class DataIngestion:
    def __init__(self, config : DataIngestionConfig , paramConfig: RAGCOnfig):
        self.config = config
        self.paramConfig = paramConfig
        load_dotenv()
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f'{self.device} is in use')
        self.embedding = SentenceTransformerEmbeddings(model_name=self.paramConfig.sentence_model)
        logger.info('Embeddings initialized')

    def load_docs_in_vectorStore(self, uploaded_files: List[UploadFile] = None):
        """
        Load documents from the local directory or UI upload, split them, and insert into Pinecone.
        """
        documents = []
        
        # Load documents from the UI
        if uploaded_files:
            for file in uploaded_files:
                try:
                    file_path = f"{file.filename}"
                    with open(file_path, "wb") as f:
                        f.write(file.file.read())
                    
                    logger.info(f'File {file.filename} saved temporarily')
                    
                    # Load PDF from temp storage
                    loader = PyMuPDFLoader(file_path)
                    documents.extend(loader.load())
                    
                    # Remove temp file after loading
                    os.remove(file_path)
                    
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error processing {file.filename}: {e}")
        
        # Load documents from the local directory
        # if not uploaded_files:
        #     loader = DirectoryLoader(
        #         self.config.get_docs,
        #         glob="*.pdf",
        #         recursive=True,
        #         loader_cls=PyMuPDFLoader
        #     )
        #     documents = loader.load()

        logger.info(f'{len(documents)} documents loaded')

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        splitted_documents = text_splitter.split_documents(documents)
        logger.info(f'{len(splitted_documents)} documents split into chunks')

        # Insert into Pinecone vector store
        index_name = self.paramConfig.pinecone_index
        vectorstore = PineconeVectorStore.from_documents(
            splitted_documents,
            index_name=index_name,
            embedding=self.embedding
        )
        
        logger.info('Documents successfully indexed in Pinecone')
        return {"status": "success", "message": "Documents added to vector store"}

            
            
        
        

        
            
        
        
