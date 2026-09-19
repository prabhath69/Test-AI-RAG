import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from agent import app as agent_app

app = FastAPI(title="Aster & Row AI Agent")

# Serve static files (HTML, CSS, JS)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]] # list of {"role": "user"|"assistant", "content": "..."}

@app.get("/", response_class=HTMLResponse)
async def index():
    index_path = os.path.join(static_dir, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/chat")
async def chat(req: ChatRequest):
    # Convert request messages to Langchain messages
    lc_messages = []
    for m in req.messages:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            lc_messages.append(AIMessage(content=m["content"]))
            
    # Run the graph
    inputs = {"messages": lc_messages}
    result = agent_app.invoke(inputs)
    
    # Get the last AI message
    final_messages = result["messages"]
    last_ai_message = final_messages[-1].content
    
    # We can also extract the tool calls and context to return as debug info
    # for observability if needed.
    
    return {"response": last_ai_message}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
