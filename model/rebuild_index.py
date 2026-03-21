"""
rebuild_index.py
----------------
Rebuilds the FAISS index using the FULL prayer text:
  title + meaning + background

Run this once (or any time dua_api.json changes):
    python model/rebuild_index.py

Outputs:
  - model/dua_model.faiss   (the new FAISS index)
  - json/index_map.json     (list of prayer IDs in FAISS order)
"""

import json
import sys
import os

# Make sure we can import from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

# ── Load prayers ──────────────────────────────────────────────────────────────
DATA_FILE   = "json/dua_api.json"
INDEX_FILE  = "model/dua_model.faiss"
MAP_FILE    = "json/index_map.json"
MODEL_NAME  = "sentence-transformers/all-MiniLM-L6-v2"
CACHE_DIR   = "./all-MiniLM-L6-v2"

print("Loading prayers from", DATA_FILE)
with open(DATA_FILE, "r", encoding="utf-8") as f:
    prayers = json.load(f)

# ── Build full-text corpus ────────────────────────────────────────────────────
# Combine title + meaning + background so the model understands intent,
# not just keyword matches on the title alone.
corpus = []
prayer_ids = []  # parallel list: corpus[i] belongs to prayer_id[i]

for prayer in prayers:
    title      = prayer.get("title", "")
    meaning    = prayer.get("meaning", "")
    background = prayer.get("background", "")
    combined   = f"{title}. {meaning}. {background}".strip()
    corpus.append(combined)
    prayer_ids.append(prayer["id"])

print(f"  {len(corpus)} prayers indexed")

# ── Encode ────────────────────────────────────────────────────────────────────
print("Loading sentence-transformer model...")
model = SentenceTransformer(MODEL_NAME, cache_folder=CACHE_DIR, device="cpu")

print("Encoding full prayer texts (this may take a moment)...")
embeddings = model.encode(corpus, show_progress_bar=True, convert_to_numpy=True)

# L2-normalise for cosine similarity via inner product
embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

# ── Build & save FAISS index ──────────────────────────────────────────────────
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)   # Inner Product == cosine (after normalising)
index.add(embeddings)                  # type: ignore

faiss.write_index(index, INDEX_FILE)
print(f"FAISS index saved → {INDEX_FILE}  ({index.ntotal} vectors)")

# ── Save ID mapping ───────────────────────────────────────────────────────────
with open(MAP_FILE, "w", encoding="utf-8") as f:
    json.dump(prayer_ids, f)
print(f"ID map saved      → {MAP_FILE}")

print("\nDone! Restart your FastAPI server to use the new index.")
