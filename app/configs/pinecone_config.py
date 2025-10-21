import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "linkedin-posts")
EMBEDDING_DIMENSION = 768

pc = Pinecone(api_key=PINECONE_API_KEY)

def init_pinecone_index():
    existing_indexes = [idx["name"] for idx in pc.list_indexes()]

    if INDEX_NAME not in existing_indexes:
        print(f"🪶 Creating Pinecone index '{INDEX_NAME}' with dimension {EMBEDDING_DIMENSION}")
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT),
        )

    index = pc.Index(INDEX_NAME)
    print(f"✅ Pinecone index '{INDEX_NAME}' initialized successfully.")
    return index


pinecone_index = init_pinecone_index()
