from dataclasses import dataclass
from pathlib import  Path

@dataclass
class DataIngestionConfig:
    root_dir : Path
    get_docs : Path
    
@dataclass
class RAGCOnfig:
    model : Path
    tokenizer : Path
    top_k :Path
    num_ctx : Path
    num_predict : Path
    temperature :Path
    top_p : Path
    sentence_model : Path
    pinecone_index : Path
    index_top_k : Path
    