import json
import numpy as np
import faiss
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

INDEX_PATH = "faiss/faiss_index.index"
METADATA_PATH = "faiss/faiss_metadata.json"

# Generate vector embeddings using Gemini
def get_embedding(text):
    response = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return np.array(response['embedding'], dtype=np.float32)

# Build the FAISS index from training JSON
def build_index(json_path='data/interview_data.json'):
    with open(json_path, 'r') as f:
        data = json.load(f)

    raw_examples = []

    # Extract Q:A → follow-up from conversation turns
    for conv in data:
        turns = conv["conversation"]
        for i in range(0, len(turns) - 2, 2):
            if turns[i]["speaker"].lower().startswith("interviewer") and \
               turns[i+1]["speaker"].lower().startswith("candidate") and \
               turns[i+2]["speaker"].lower().startswith("interviewer"):

                q = turns[i]["text"]
                a = turns[i+1]["text"]
                follow_up = turns[i+2]["text"]
                qa_text = f"Q: {q}\nA: {a}"

                raw_examples.append({
                    "text": qa_text,
                    "next_question": follow_up
                })

    # Deduplicate based on Q:A and follow-up
    seen = set()
    unique_data = []
    for item in raw_examples:
        signature = (item['text'], item.get('next_question', ''))
        if signature not in seen:
            seen.add(signature)
            unique_data.append(item)

    # Embed and build index
    vectors, metadata = [], []
    for item in unique_data:
        vec = get_embedding(item['text'])
        vectors.append(vec)
        metadata.append(item)

    vectors = np.vstack(vectors)
    dim = vectors.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    os.makedirs("faiss", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(METADATA_PATH, 'w') as f:
        json.dump(metadata, f)

    print(f"✅ FAISS index built and saved with {len(metadata)} unique QA pairs.")

# Load FAISS index and metadata
def load_index():
    index = faiss.read_index(INDEX_PATH)
    with open(METADATA_PATH, 'r') as f:
        metadata = json.load(f)
    return index, metadata

# Retrieve most similar QA-follow-up pairs
def retrieve_similar(query, top_k=3):
    query_vec = get_embedding(query).reshape(1, -1)
    index, metadata = load_index()
    distances, indices = index.search(query_vec, top_k)

    # Optional deduplication in retrieval (if needed)
    seen = set()
    results = []
    for i in indices[0]:
        item = metadata[i]
        sig = (item["text"], item.get("next_question", ""))
        if sig not in seen:
            seen.add(sig)
            results.append(item)
    return results
