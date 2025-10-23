from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
from model.model2 import model, Index, keys
import numpy as np


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers = ["*"]
)


datas = []
dua_data = {}
index = Index

with open("json/dua_api.json","rb") as f:
    datas = json.load(f)

with open("json/data_keys.json",'rb') as ff:
    dua_data = json.load(ff)

def get_result(question,top_k=3):
    question_embeddings = model.encode([question])
    question_embeddings = question_embeddings / np.linalg.norm(question_embeddings,axis=1,keepdims=True)
    distances,indices = index.search(np.array(question_embeddings),top_k)  #type: ignore
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