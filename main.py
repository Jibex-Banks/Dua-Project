from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

datas = []
dua_data = {}

with open("json/dua_api.json", "r", encoding="utf-8") as f:
    datas = json.load(f)

with open("json/data_keys.json", "r", encoding="utf-8") as ff:
    dua_data = json.load(ff)

def get_result(question, top_k=1):
    question_embeddings = model.encode([question])
    question_embeddings = question_embeddings / np.linalg.norm(question_embeddings, axis=1, keepdims=True)
    distances, indices = index.search(np.array(question_embeddings, dtype=np.float32), top_k)
    results = [n_keys[i] for i in indices[0]]
    return results


class Prompt(BaseModel):
    question: str


@app.on_event("startup")
async def startup_event():
    from sentence_transformers import SentenceTransformer
    import faiss
    from model.model2 import keys
    global model, index, n_keys
    n_keys = keys
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2",cache_folder="./all-MiniLM-L6-v2", device="cpu")
    index = faiss.read_index("model/dua_model.faiss")


@app.get('/')
async def home():
    return {"message": "Welcome To Moon 🌙 - Technology driven by Faith"}


@app.post("/query")
async def query(prompt: Prompt):
    try:
        question = prompt.question
        keys = get_result(question)
        response = []

        for key in keys:
            idx = dua_data[key]
            for data in datas:
                if data["id"] == idx:
                    response.append(data)

        if not response:
            raise HTTPException(status_code=404, detail="No results found")

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Moon encountered an internal error: {e}")
