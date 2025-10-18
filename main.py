from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model.model2 import keys
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

# Make model and index global
model = None
index = None
datas = []
dua_data = {}

# Proper lifespan event for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, index  # 👈 must declare globals here
    print("🚀 Loading model and index...")
    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        cache_folder="./all-MiniLM-L6-v2"
    )
    index = faiss.read_index("model/dua_model.faiss")
    print("✅ Model and FAISS index loaded.")
    yield
    print("👋 Shutting down...")

# Initialize app with lifespan
app = FastAPI(lifespan=lifespan)

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Load your JSON data
with open("json/dua_api.json", "rb") as f:
    datas = json.load(f)

with open("json/data_keys.json", "rb") as ff:
    dua_data = json.load(ff)

def get_result(question, top_k=3):
    question_embeddings = model.encode([question])
    question_embeddings = question_embeddings / np.linalg.norm(question_embeddings, axis=1, keepdims=True)
    distances, indices = index.search(np.array(question_embeddings), top_k)
    results = [keys[i] for i in indices[0]]
    return results

class Prompt(BaseModel):
    question: str

@app.get("/")
async def home():
    return {"message": "Welcome To Moon, Technology driven by Faith"}

@app.post("/query")
async def query(prompt: Prompt):
    response = []
    try:
        question = prompt.question
        matched_keys = get_result(question)
        for key in matched_keys:
            index_value = dua_data[key]
            for data in datas:
                if data["id"] == index_value:
                    response.append(data)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Moon encountered an error: {e}"
        )

# 👇 Add this so Render knows what port to use
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
