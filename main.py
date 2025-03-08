from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from nextcloud_client import NextCloudClient
from llm_provider import get_llm_provider

# Load environment variables
load_dotenv()

app = FastAPI(title="NextCloud MCP Server")

# Initialize NextCloud client with the shared folder URL
NEXTCLOUD_SHARE_URL = "https://cloud.monadical.com/s/EE7yBz8tF85kMsw"
nextcloud_client = NextCloudClient(NEXTCLOUD_SHARE_URL)

class Query(BaseModel):
    text: str
    provider: Optional[str] = "openai"
    api_key: Optional[str] = None

@app.post("/query")
async def process_query(query: Query):
    try:
        # Get context from NextCloud
        context = nextcloud_client.build_context()
        
        # Get the specified LLM provider
        llm = get_llm_provider(query.provider, query.api_key)
        
        # Process the query
        response = llm.process_query(query.text, context)
        
        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/providers")
async def list_providers():
    """List available LLM providers."""
    return {"providers": ["openai", "anthropic"]}

@app.get("/files")
async def list_files():
    """List available files in the NextCloud shared folder."""
    files = nextcloud_client.list_files()
    return {"files": files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)