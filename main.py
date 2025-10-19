from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from model.model2 import keys
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os


@asynccontextmanager # type: ignore
async def lifespan(app : FastAPI):
    global model,index
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2",cache_folder="./all-MiniLM-L6-v2")
    index = faiss.read_index("model/dua_model.faiss")
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers = ["*"]
)


datas = []
dua_data = {}

with open("json/dua_api.json","rb") as f:
    datas = json.load(f)

with open("json/data_keys.json",'rb') as ff:
    dua_data = json.load(ff)

def get_result(question,top_k=3):
    question_embeddings = model.encode([question])
    question_embeddings = question_embeddings / np.linalg.norm(question_embeddings,axis=1,keepdims=True)
    distances,indices = index.search(np.array(question_embeddings),top_k)
    results = [keys[i] for i in indices[0]]
    response = [result for result in results]
    return response


class Prompt(BaseModel):
    question : str

# http://127.0.0.1:8000/
@app.get('/')
async def home():
    return {"message":"Welcome To Moon, Technology driven by Faith"}

# http://127.0.0.1:8000/query
@app.post("/query")
async def query(prompt:Prompt):
    response = []
    try:
        question = prompt.question
        keys = get_result(question)
        for key in keys:
            index = dua_data[key]
            for data in datas:
                if data["id"] == index:   
                    response.append(data)
                else:
                    pass
            return response
    except Exception as e:
        raise HTTPException(status_code=301,detail=f"Moon as being Attacked due to this reason <{e}>,Please resolve immediately!")
    
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)