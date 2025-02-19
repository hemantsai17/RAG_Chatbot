from src.RAG_Chatbot.constants import *
from src.RAG_Chatbot.utils.common import *
from src.RAG_Chatbot.entity import DataIngestionConfig , RAGCOnfig


class ConfigurationManagerDI:
    def __init__(self , params_path=PARAMS_YAMLPATH , config_path=CONFIG_YAMLPATH):
        self.config = read_yaml(config_path)
        self.params = read_yaml(params_path)
        
        create_directories([self.config.artifacts_root ])
        
    def get_data_ingestion_config(self) -> DataIngestionConfig:
        get_config = self.config.data_ingestion
        create_directories([get_config.root_dir])
        
        get_data_ingestion_config = DataIngestionConfig(
            root_dir=get_config.root_dir,
            get_docs=get_config.get_docs
            
        )
        
        return get_data_ingestion_config

class RAGCOnfigurationManager:
    def __init__(self , config_path =CONFIG_YAMLPATH , params_path=PARAMS_YAMLPATH):
        self.config = read_yaml(config_path)
        self.params = read_yaml(params_path)
        
        create_directories([self.config.artifacts_root])
        
    def get_rag_config(self) -> RAGCOnfig:
        get_rag_config1 = self.config.RAG
        get_param_config1 = self.params.PARAM
        get_pinecone_config = self.params.PINECONE
            
        ragConfigurations = RAGCOnfig(model=get_rag_config1.model, 
                                    tokenizer=get_rag_config1.tokenizer,
                                    top_k=get_param_config1.top_k,
                                    top_p=get_param_config1.top_p,
                                    num_ctx=get_param_config1.num_ctx,
                                    num_predict=get_param_config1.num_predict,
                                    temperature=get_param_config1.temperature,
                                    sentence_model=get_rag_config1.sentence_model,
                                    pinecone_index=get_pinecone_config.index_name,
                                    index_top_k=get_pinecone_config.index_top_k)
            
        return ragConfigurations