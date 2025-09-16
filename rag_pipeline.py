# rag_pipeline.py
import os
import logging
from typing import List, Dict, Tuple
import numpy as np
import pandas as pd
import faiss
from openai import OpenAI
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from huggingface_hub import hf_hub_download
from dotenv import load_dotenv

# =====================
# Load environment
# =====================
load_dotenv()  # local only; Render injects ENV vars automatically

LOGGER = logging.getLogger("rag_pipeline")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Add it to your .env or Render environment.")

client = OpenAI(api_key=OPENAI_API_KEY)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
DECOMPOSE_MODEL = os.getenv("DECOMPOSE_MODEL", "gpt-4o-mini")
ANSWER_MODEL = os.getenv("ANSWER_MODEL", "gpt-4o-mini")

# =====================
# Hugging Face files
# =====================
HF_REPO = "PotatoUmair/drug-rag-data1"  # change if you upload to another repo

def download_file(filename: str) -> str:
    """Download file from Hugging Face Hub and return local path."""
    LOGGER.info("Downloading %s from Hugging Face Hub...", filename)
    path = hf_hub_download(repo_id=HF_REPO, filename=filename)
    LOGGER.info("Downloaded %s to %s", filename, path)
    return path

INDEX_FILE = download_file("drug_embeddings.faiss")
METADATA_FILE = download_file("drug_chunks_metadata.csv")
# Optional: If you ever use embeddings.npy
# EMBEDDINGS_FILE = download_file("embedding.npy")

# =====================
# Load FAISS + Metadata
# =====================
LOGGER.info("Loading FAISS index from %s", INDEX_FILE)
_index = faiss.read_index(INDEX_FILE)

LOGGER.info("Loading metadata from %s", METADATA_FILE)
_metadata = pd.read_csv(METADATA_FILE)

# =====================
# Retry Decorator
# =====================
retry_decorator = retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=1, max=20),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(Exception)
)

# =====================
# Embedding Function
# =====================
@retry_decorator
def _create_embedding(text: str) -> np.ndarray:
    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    emb = np.array(resp.data[0].embedding, dtype="float32")
    return emb

# =====================
# Chat Completion Wrapper
# =====================
@retry_decorator
def _llm_chat_completion(prompt: str, model: str, temperature: float = 0.0) -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return resp.choices[0].message.content.strip()

# =====================
# Pipeline Steps
# =====================
def decompose_query(user_query: str, max_subqueries: int = 5) -> List[str]:
    prompt = f"""
You are an expert in drug information. Split the following user query into up to {max_subqueries} independent sub-questions.
Return each sub-question on a separate line.

User query: "{user_query}"
"""
    try:
        text = _llm_chat_completion(prompt, model=DECOMPOSE_MODEL, temperature=0.0)
        sub_queries = [q.strip() for q in text.splitlines() if q.strip()]
        return sub_queries or [user_query]
    except Exception as exc:
        LOGGER.exception("Decomposition failed; using original query. Error: %s", exc)
        return [user_query]

def retrieve_chunks(query_text: str, top_k: int = 3) -> List[Dict]:
    try:
        emb = _create_embedding(query_text)
    except Exception as exc:
        LOGGER.exception("Embedding creation failed: %s", exc)
        return []

    emb = emb.reshape(1, -1).astype("float32")
    distances, indices = _index.search(emb, top_k)
    results = []
    for idx, dist in zip(indices[0], distances[0]):
        if idx < 0 or idx >= len(_metadata):
            continue
        row = _metadata.iloc[int(idx)]
        results.append({
            "drug_name": row.get("drug_name"),
            "drugbank_id": row.get("drugbank_id"),
            "chunk_index": int(row.get("chunk_index")) if "chunk_index" in row else None,
            "text": row.get("chunk_text"),
            "distance": float(dist)
        })
    return results

def generate_answer(sub_query: str, chunks: List[Dict]) -> str:
    if not chunks:
        return "No relevant information found."
    prompt_chunks = "\n\n".join([f"Chunk: {c['text']}" for c in chunks])
    prompt = f"""
You are a medical expert. Answer the question below using ONLY the information from the retrieved chunks.
Do not make assumptions or hallucinate. Be concise and precise.

{prompt_chunks}

Question: {sub_query}
Answer:
"""
    try:
        return _llm_chat_completion(prompt, model=ANSWER_MODEL, temperature=0.0)
    except Exception as exc:
        LOGGER.exception("Answer generation failed for '%s': %s", sub_query, exc)
        return "Error generating answer."

def combine_answers(user_query: str, sub_query_answers: List[Dict]) -> str:
    combined_text = "\n".join([f"{i+1}. {a['answer']}" for i, a in enumerate(sub_query_answers)])
    prompt = f"""
You are a medical expert. The user asked the following question:

{user_query}

Here are the answers to sub-questions:

{combined_text}

Combine these into a single, concise, coherent answer. Only use the provided information.
Final Answer:
"""
    try:
        return _llm_chat_completion(prompt, model=ANSWER_MODEL, temperature=0.0)
    except Exception as exc:
        LOGGER.exception("Final answer combination failed: %s", exc)
        return "Error generating final answer."

def query_pipeline(user_query: str, top_k: int = 3, max_subqueries: int = 5) -> Tuple[str, List[Dict]]:
    sub_queries = decompose_query(user_query, max_subqueries=max_subqueries)
    answers = []
    for sq in sub_queries:
        chunks = retrieve_chunks(sq, top_k=top_k)
        answer = generate_answer(sq, chunks)
        answers.append({"sub_query": sq, "answer": answer, "chunks": chunks})
    final_answer = combine_answers(user_query, answers)
    return final_answer, answers
