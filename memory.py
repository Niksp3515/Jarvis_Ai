memory_texts = []

def store_memory(text):
    memory_texts.append(text)
    # Keep only the last 15 interactions to prevent excessive token burning
    if len(memory_texts) > 15:
        memory_texts.pop(0)

def retrieve_memory(query, k=3):
    if not memory_texts:
        return ""
    # Since we want context, just return the last `k` interactions seamlessly
    return "\n".join(memory_texts[-k:])