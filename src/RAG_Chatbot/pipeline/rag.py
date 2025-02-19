import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


from src.RAG_Chatbot.config.configuration import RAGCOnfigurationManager
from src.RAG_Chatbot.components.rag_working import *
import os

print("OLLAMA_HOST:", os.getenv("OLLAMA_HOST"))



class RAGPipeline:
    def __init__(self):
        config_manager = RAGCOnfigurationManager()
        self.config = config_manager.get_rag_config()

    async def getanswer(self, user_input):
        
        rag_working = RAGWORKING(config=self.config)
        
        # Call the async generator method properly
        async for chunk in rag_working.conversational_rag_chain(user_input):
            yield chunk  # Yield the streaming response chunk-by-chunk
