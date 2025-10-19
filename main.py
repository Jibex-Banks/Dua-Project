from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers = ["*"]
)


# http://127.0.0.1:8000/
@app.get('/')
async def home():
    return {"message":"Welcome To Moon, Technology driven by Faith"}


# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8000))
#     uvicorn.run(app, host="0.0.0.0", port=port)