from src.RAG_Chatbot.constants import CONFIG_YAMLPATH , PARAMS_YAMLPATH
from src.RAG_Chatbot.utils.common import *
from src.RAG_Chatbot.entity import *
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline ,AutoModelForCausalLM, BitsAndBytesConfig

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.vectorstores import Pinecone
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from langchain.chains import LLMChain
import streamlit as st
from langchain.schema import HumanMessage
from langchain.chains import RetrievalQA
from functools import lru_cache
import torch




from dotenv import load_dotenv
import os



class RAGWORKING:
    def __init__(self , config = RAGCOnfig):
        self.config = config
        
    
    def rag_template_model(self):
        
        
        prompt_template = """
            <|begin_of_text|>
            <|start_header_id|>system<|end_header_id|>
            **System Prompt:**  
            You are a knowledgeable and context-aware assistant. Your goal is to provide well-structured, clear, and factually accurate answers **only from the given context**. If the context does not contain relevant information, respond with "I do not have enough information to answer this question."  

            Your responses must follow this structured format:  

            1. **Introduction:** Provide a brief overview of the topic, setting the context.  
            2. **Detailed Explanation:** Break down the topic into logical subpoints, explaining each concept clearly using bullet points if necessary.  
            3. **Examples:** Include relevant real-world examples to illustrate key ideas.  
            4. **Conclusion:** Summarize the discussion concisely.  

            ### **Example Response Format:**  

            **User Question:** What is Artificial Intelligence?  

            **Expected Model Response:**  
            Artificial Intelligence (AI) refers to the simulation of human intelligence in machines, allowing them to perform tasks that typically require human reasoning, learning, and decision-making. AI enables automation and efficiency across various industries, making it a key technological advancement.  

            AI can be categorized into different fields:  

            - **Machine Learning (ML):** AI that learns patterns from data to improve performance without explicit programming.  
            - **Natural Language Processing (NLP):** AI that enables computers to understand and generate human language, used in applications like chatbots and translation tools.  
            - **Computer Vision:** AI systems that interpret and process visual information from images or videos.  
            - **Expert Systems:** AI designed to mimic human decision-making in specialized fields such as healthcare and finance.  

            **Example:** Virtual assistants like Siri and Google Assistant use NLP to understand and respond to human speech. Self-driving cars utilize AI for real-time decision-making based on environmental data.  

            In conclusion, AI is a transformative technology that continues to evolve, impacting multiple industries and everyday life.  

            ---

            ### **Response Guidelines:**  
            - **Only use information from the provided context.** If the context does not contain an answer, state: "I do not have enough information to answer this question."  
            - **Use markdown formatting** (e.g., `**bold**`, `- bullet points`) for structured and readable responses.  
            - **Never return raw HTML, LaTeX, or unformatted text.** Only use markdown.  
            - **Do not hallucinate information** beyond the given context.  

            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            {user_prompt}
            <|eot_id|>
            <|start_header_id|>context<|end_header_id|>
            {context}
            <|eot_id|>

            """


        
        template_prompt = PromptTemplate(input_variables=["question", "context"], template=prompt_template)




        
        return template_prompt
    
   
    
    async def conversational_rag_chain(self , user_input ):
        torch.cuda.empty_cache()
        
        
        os.getenv("OLLAMA_HOST")
        ollama_url = os.environ.get('OLLAMA_HOST')
        pinecone_api = os.environ.get("PINECONE_API_KEY")
        
        print("Using Ollama URL:", ollama_url)
        print("using pincone url:",pinecone_api )

        
        @lru_cache(maxsize=1)
        def load_model():
            
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../installed_model"))

            # Define paths for tokenizer and model
            tokenizer_path = os.path.join(base_path, "Llama-3.2-3B-Instruct-tokenzer")
            model_path = os.path.join(base_path, "Llama-3.2-3B-Instruct")
            
            # model_name1 = "meta-llama/Llama-3.2-3B-Instruct"
            
            model = ChatOllama(base_url=ollama_url,model="llama3.2:3b" ,num_predict=self.config.num_predict , num_ctx=self.config.num_ctx , 
                               top_k=self.config.top_k , top_p=self.config.top_p , temperature=self.config.temperature)
            
            # tokenizer = AutoTokenizer.from_pretrained(model_name1 ,truncation=True , padding=True)
            # model = AutoModelForCausalLM.from_pretrained(model_name1 , quantization_config=bnb_config)
        
            return model 
        
        @lru_cache(maxsize=1)
        def load_sentence_transformer():
            'cuda' if torch.cuda.is_available() else "cpu"
            
            embedding = SentenceTransformerEmbeddings(model_name=self.config.sentence_model)
        
            return embedding
        
        
        # Example inputs
        # context = "The population of Paris is approximately 2.1 million in 2023."
        # conversation_history = "Human: What is the capital of France?\nAI: The capital of France is Paris."
        # question = "What is the current population of Paris?"

        # Use the template to generate a formatted prompt
        
        llama_model= load_model()
        # Now you can pass the generated prompt to the model (like LLaMA or any conversational model)
        
        sentence_embedding = load_sentence_transformer()
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        template_prompt = self.rag_template_model()

        load_dotenv()
        
        os.getenv("PINECONE_API_KEY")
        
        pinecone_api_key = os.environ.get("PINECONE_API_KEY")
        
        print('pinecone api' , pinecone_api_key)
        # embedding = SentenceTransformerEmbeddings(model_name=sentence_embedding,model_kwargs={"device": device})

        vector_store = Pinecone.from_existing_index(index_name=self.config.pinecone_index, embedding=sentence_embedding)
        
        # retriever = vector_store.as_retriever(search_kwargs={"k": self.config.index_top_k})
        context_docs= vector_store.max_marginal_relevance_search(query=user_input , k=self.config.index_top_k , lambda_mult=0.5)
        
        
        # context_docs = retriever.get_relevant_documents(user_input)
        
      
    
        if not context_docs:
            raise ValueError("No relevant documents retrieved for the query.")
    
    
        context = " ".join([f'\n Document :::\n' + doc.page_content for doc in context_docs if doc.page_content])


        print("Context Length:", len(context.split()))
        print("Context:", context)
    
        if not context:
            raise ValueError("Context is empty after combining retrieved documents.")
        
    
        formatted_input = template_prompt.format(user_prompt=user_input, context=context)


       
        async for chunk in llama_model.astream(formatted_input):
            yield chunk.content
      
    
    
        