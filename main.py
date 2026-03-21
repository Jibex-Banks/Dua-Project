from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the sentence-transformer model and FAISS index on startup."""
    from sentence_transformers import SentenceTransformer
    import faiss as _faiss
    global nlp_model, faiss_index
    nlp_model   = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        cache_folder="./all-MiniLM-L6-v2",
        device="cpu"
    )
    faiss_index = _faiss.read_index("model/dua_model.faiss")
    print(f"FAISS index loaded — {faiss_index.ntotal} prayers indexed")
    yield  # app runs here


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Load prayer data & index map at module level ───────────────────────────────
# prayers_by_id: dict[int, dict]  — fast lookup by prayer ID
prayers_by_id = {}
with open("json/dua_api.json", "r", encoding="utf-8") as f:
    for p in json.load(f):
        prayers_by_id[p["id"]] = p

# index_map: list[int] — index_map[i] == prayer ID at FAISS position i
index_map: list = []
try:
    with open("json/index_map.json", "r", encoding="utf-8") as f:
        index_map = json.load(f)
except FileNotFoundError:
    pass  # Will fail gracefully at query time if missing


# ── NLP search ────────────────────────────────────────────────────────────────

def get_result(question: str, top_k: int = 3) -> list[dict]:
    """
    Encode the question with the same model used to build the index,
    search the FAISS index, and return the top_k matching prayer objects.
    """
    if not index_map:
        raise RuntimeError(
            "index_map.json not found. "
            "Run `python model/rebuild_index.py` first."
        )

    q_emb = nlp_model.encode([question], convert_to_numpy=True)
    q_emb = q_emb / np.linalg.norm(q_emb, axis=1, keepdims=True)
    _, indices = faiss_index.search(np.array(q_emb, dtype=np.float32), top_k)

    results = []
    for i in indices[0]:
        if i < 0 or i >= len(index_map):
            continue
        prayer_id = index_map[i]
        prayer = prayers_by_id.get(prayer_id)
        if prayer:
            results.append(prayer)
    return results


# ── Models ────────────────────────────────────────────────────────────────────

class Prompt(BaseModel):
    question: str

class Feedback(BaseModel):
    name: str = "Anonymous"
    message: str


# ── Home ──────────────────────────────────────────────────────────────────────

@app.get("/")
async def home():
    return {"message": "Welcome To Moon \U0001f319 - Technology driven by Faith"}


# ── Query ─────────────────────────────────────────────────────────────────────

@app.post("/query")
async def query(prompt: Prompt):
    """
    Natural language prayer search.
    The model searches title + meaning + background of every prayer.

    Example: {"question": "I feel sick and need healing"}
    """
    try:
        results = get_result(prompt.question, top_k=3)
        if not results:
            raise HTTPException(status_code=404, detail="No matching prayers found.")
        return results
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Moon encountered an error: {e}")


# ── Visitor Counter ───────────────────────────────────────────────────────────

VISITORS_FILE = "json/visitors.json"


def _load_visitors() -> int:
    try:
        with open(VISITORS_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("count", 0)
    except FileNotFoundError:
        return 0


def _save_visitors(count: int):
    with open(VISITORS_FILE, "w", encoding="utf-8") as f:
        json.dump({"count": count}, f)


@app.get("/visit")
async def visit():
    """Increment and return the visitor count. Call when a user opens the site."""
    count = _load_visitors() + 1
    _save_visitors(count)
    return {"visitors": count}


@app.get("/visitors")
async def get_visitors():
    """Read-only: returns the current visitor count without incrementing."""
    return {"visitors": _load_visitors()}


# ── Feedback ──────────────────────────────────────────────────────────────────

FEEDBACK_FILE = "json/feedback.json"


def _load_feedback() -> list:
    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def _save_feedback(entries: list):
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


@app.post("/feedback")
async def submit_feedback(feedback: Feedback):
    """Submit feedback. Name optional (defaults to Anonymous). Message required."""
    if not feedback.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    from datetime import datetime, timezone
    entry = {
        "name": feedback.name.strip() or "Anonymous",
        "message": feedback.message.strip(),
        "submitted_at": datetime.now(timezone.utc).isoformat()
    }
    entries = _load_feedback()
    entries.append(entry)
    _save_feedback(entries)
    return {"success": True, "message": "Thank you for your feedback! \U0001f319"}


@app.get("/feedback")
async def get_feedback():
    """Returns all submitted feedback entries."""
    return _load_feedback()
