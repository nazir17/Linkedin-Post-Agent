import os
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
from dotenv import load_dotenv

load_dotenv()

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME", "linkedin_posts")

EMBEDDING_DIMENSION = 768


def init_milvus():
    try:
        connections.connect(
            alias="default",
            host=MILVUS_HOST,
            port=MILVUS_PORT
        )
        print(f"Connected to Milvus at {MILVUS_HOST}:{MILVUS_PORT}")
    except Exception as e:
        print(f"Failed to connect to Milvus: {e}")
        raise

    if utility.has_collection(COLLECTION_NAME):
        print(f"Collection '{COLLECTION_NAME}' already exists")
        collection = Collection(COLLECTION_NAME)

        for field in collection.schema.fields:
            if field.name == "embedding" and field.params.get("dim") != EMBEDDING_DIMENSION:
                print(f"Dimension mismatch! Dropping collection...")
                utility.drop_collection(COLLECTION_NAME)
                collection = create_collection()
                break
    else:
        collection = create_collection()

    collection.load()
    print(f"Collection '{COLLECTION_NAME}' loaded")
    
    return collection


def create_collection():

    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIMENSION),
        FieldSchema(name="topic", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="content_preview", dtype=DataType.VARCHAR, max_length=1000),
    ]
    
    schema = CollectionSchema(
        fields=fields,
        description="LinkedIn posts embeddings"
    )

    collection = Collection(
        name=COLLECTION_NAME,
        schema=schema,
        using='default'
    )
    
    print(f"Created collection '{COLLECTION_NAME}' with dimension {EMBEDDING_DIMENSION}")

    index_params = {
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    
    collection.create_index(
        field_name="embedding",
        index_params=index_params
    )
    
    print(f"Created index for collection '{COLLECTION_NAME}'")
    
    return collection

milvus_collection = init_milvus()