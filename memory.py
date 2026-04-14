import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 🔹 Load embedding model
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

# 🔹 FAISS index
dimension = 384
index = faiss.IndexFlatL2(dimension)

# 🔹 Memory storage
memory_texts = []


# ✅ Store memory
def store_memory(text):
    embedding = embed_model.encode([text])
    embedding = np.array(embedding).astype('float32')

    index.add(embedding)
    memory_texts.append(text)


# ✅ Retrieve memory
def retrieve_memory(query, k=3):
    if len(memory_texts) == 0:
        return ""

    query_embedding = embed_model.encode([query])
    query_embedding = np.array(query_embedding).astype('float32')

    distances, indices = index.search(query_embedding, k)

    results = []
    for i in indices[0]:
        if i < len(memory_texts):
            results.append(memory_texts[i])

    # remove duplicates
    return "\n".join(list(set(results)))