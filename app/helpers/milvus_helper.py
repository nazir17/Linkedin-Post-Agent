from app.configs.milvus_config import milvus_collection
from typing import List, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


def upsert_vectors(vectors: List[Tuple[str, List[float], Dict[str, Any]]]) -> Dict:
    try:
        ids = []
        embeddings = []
        topics = []
        content_previews = []
        
        for vec in vectors:
            if isinstance(vec, (tuple, list)):
                vec_id = str(vec[0])
                embedding = vec[1]
                metadata = vec[2] if len(vec) > 2 else {}
            elif isinstance(vec, dict):
                vec_id = str(vec["id"])
                embedding = vec["values"]
                metadata = vec.get("metadata", {})
            else:
                raise ValueError(f"Invalid vector format: {type(vec)}")

            if not isinstance(embedding, list):
                embedding = list(embedding)
            embedding = [float(x) for x in embedding]
            
            ids.append(vec_id)
            embeddings.append(embedding)
            topics.append(metadata.get("topic", ""))
            content_previews.append(metadata.get("content_preview", ""))

        try:
            expr = f'id in {ids}'
            milvus_collection.delete(expr)
        except Exception as e:
            logger.debug(f"No existing records to delete: {e}")

        data = [
            ids,
            embeddings,
            topics,
            content_previews
        ]
        
        result = milvus_collection.insert(data)

        milvus_collection.flush()
        
        logger.info(f"Milvus: Upserted {len(ids)} vector(s)")
        
        return {
            "insert_count": result.insert_count,
            "ids": ids
        }
        
    except Exception as e:
        logger.error(f"Milvus upsert error: {e}")
        raise


def query_similar(vector: List[float], top_k: int = 5) -> List[Dict]:
    try:
        if not isinstance(vector, list):
            vector = list(vector)
        
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        
        results = milvus_collection.search(
            data=[vector],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["id", "topic", "content_preview"]
        )
        
        formatted_results = []
        for hits in results:
            for hit in hits:
                formatted_results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "metadata": {
                        "topic": hit.entity.get("topic"),
                        "content_preview": hit.entity.get("content_preview")
                    }
                })
        
        logger.info(f"Milvus: Found {len(formatted_results)} similar vectors")
        return formatted_results
        
    except Exception as e:
        logger.error(f"Milvus query error: {e}")
        raise


def get_collection_stats() -> Dict:
    try:
        stats = {
            "name": milvus_collection.name,
            "num_entities": milvus_collection.num_entities,
            "description": milvus_collection.description
        }
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {}


def delete_by_ids(ids: List[str]) -> bool:
    try:
        expr = f'id in {ids}'
        milvus_collection.delete(expr)
        milvus_collection.flush()
        logger.info(f"Deleted {len(ids)} vectors")
        return True
    except Exception as e:
        logger.error(f"Delete error: {e}")
        return False