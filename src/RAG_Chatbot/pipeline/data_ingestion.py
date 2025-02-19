from src.RAG_Chatbot.config.configuration import *
from src.RAG_Chatbot.components.docs_ingestion import *

class DataIngestionPipline:
    def __init__(self):
        configManager = ConfigurationManagerDI()
        ragConfigmanager = RAGCOnfigurationManager()
        
        self.paramConfig = ragConfigmanager.get_rag_config()

        self.config= configManager.get_data_ingestion_config()
    
    def initiate_data_ingestion(self , uploaded_files):
        

        data_ingestion = DataIngestion(config=self.config , paramConfig=self.paramConfig )

        data_ingestion.load_docs_in_vectorStore(uploaded_files)