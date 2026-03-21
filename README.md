# 🌙 Moon — Technology Driven by Faith

A FastAPI app that uses **Sentence Transformers + FAISS** to search and return dua results semantically.

### 🚀 Endpoints
- `/` — Welcome message
- `/query` — POST request with JSON `{ "question": "your text" }`

### 🧠 Model
Uses `sentence-transformers/paraphrase-MiniLM-L3-v2` on CPU.

### 🛠️ Example
```bash
curl -X POST https://<your-space>.hf.space/query \
     -H "Content-Type: application/json" \
     -d '{"question":"How can I seek forgiveness?"}'
