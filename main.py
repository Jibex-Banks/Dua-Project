from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from model.model2 import model, keys
import faiss
import numpy as np

app = FastAPI()


index = faiss.read_index("model/dua_model.faiss")

def get_result(question,top_k=1):
    question_embeddings = model.encode([question])
    question_embeddings = question_embeddings / np.linalg.norm(question_embeddings,axis=1,keepdims=True)
    distances,indices = index.search(np.array(question_embeddings),top_k)
    results = [(keys[i], distances[0][pos]) for pos,i in enumerate(indices[0])]
    return results


class Prompt(BaseModel):
    question : str

# http://127.0.0.1:8000/
@app.get('/')
async def home():
    return {"message":"Welcome To Moon, Technology driven by Faith"}

# http://127.0.0.1:8000/query
@app.post("/query")
async def query(prompt:Prompt):
    try:
        question = prompt.question
        response = get_result(question)
        return {"message":response}
    except Exception as e:
        raise HTTPException(status_code=404,detail="""
                Moon as being Attacked due to this reason
                "{e}",
                Please resolve immediately!
            """)