from fastapi import FastAPI
import uvicorn
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from src.RAG_Chatbot.pipeline.rag import RAGPipeline 
from src.RAG_Chatbot.pipeline.data_ingestion import DataIngestionPipline
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from typing import List
from sse_starlette import EventSourceResponse
from fastapi.responses import StreamingResponse
import asyncio
import os


print("OLLAMA_HOST:", os.getenv("OLLAMA_HOST"))


app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, or specify a list of allowed origins like ["http://example.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Index route to redirect to docs
@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")



@app.get("/getText")
async def get_text(text: str):
    try:
        obj = RAGPipeline()
        
        # StreamingResponse needs an async generator, so we directly return it
        return StreamingResponse(obj.getanswer(text), media_type="text/plain")

    except Exception as e:
        return {"error": f"Error Occurred: {e}"}



       
@app.post("/uploadDocs")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Endpoint to upload and inject documents into Pinecone.
    """
    try:
        doc = DataIngestionPipline()
        result = doc.initiate_data_ingestion(uploaded_files=files)
        # result = data_ingestion.load_docs_in_vectorStore(uploaded_files=files)
        print(result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app if this file is executed directly
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
