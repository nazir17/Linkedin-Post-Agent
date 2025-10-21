from app.configs.pinecone_config import pinecone_index
from typing import List, Tuple, Dict, Any


def upsert_vectors(vectors: List[Tuple[str, List[float], Dict[str, Any]]]) -> Dict:
    try:
        formatted = []
        
        for vec in vectors:
            if isinstance(vec, (tuple, list)):
                vec_id = str(vec[0])
                values = vec[1]
                metadata = vec[2] if len(vec) > 2 else {}
            elif isinstance(vec, dict):
                vec_id = str(vec["id"])
                values = vec["values"]
                metadata = vec.get("metadata", {})
            else:
                raise ValueError(f"Invalid vector format: {type(vec)}")
            
            if not isinstance(values, list):
                values = list(values)
            
            formatted.append({
                "id": vec_id,
                "values": values,
                "metadata": metadata
            })
        
        result = pinecone_index.upsert(vectors=formatted)
        
        print(f"✅ Pinecone: Upserted {result.get('upserted_count', 0)} vectors")
        return result
        
    except Exception as e:
        print(f"❌ Pinecone upsert error: {e}")
        raise


def query_similar(vector, top_k=5):
    try:
        if not isinstance(vector, list):
            vector = list(vector)
        
        result = pinecone_index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )
        return result
        
    except Exception as e:
        print(f"Pinecone query error: {e}")
        raise