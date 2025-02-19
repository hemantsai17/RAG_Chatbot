from src.RAG_Chatbot.logging import logger
from src.RAG_Chatbot.pipeline.rag import RAGPipeline


STAGE_NAME = "RAG OPERATION"

try:
    logger.info(f'Rag Working Initiated ')
    user_input = 'What is UPSC?'
    initiate_rag_working = RAGPipeline.getanswer(user_input=user_input)
    logger.info(f'Rag Working Completed ')
except Exception as e:
    logger.exception(e)