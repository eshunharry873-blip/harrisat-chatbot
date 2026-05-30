from app.config import settings
from app.logger import logger
from typing import List, Optional

class VectorService:
    def __init__(self):
        try:
            import pinecone
            pinecone.init(api_key=settings.pinecone_api_key, environment=settings.pinecone_env)
            self.index_name = "harrisat"
            if self.index_name not in pinecone.list_indexes():
                pinecone.create_index(self.index_name, dimension=1536)
            self.index = pinecone.Index(self.index_name)
        except Exception as e:
            logger.warning(f"Vector service initialization warning: {str(e)}")
            self.index = None
    
    async def store_embedding(self, text: str, metadata: dict, embedding_id: str):
        try:
            if not self.index:
                logger.warning("Vector index not available")
                return
            
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            response = client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            embedding = response.data[0].embedding
            self.index.upsert([(embedding_id, embedding, metadata)])
            logger.info(f"Embedding stored: {embedding_id}")
        except Exception as e:
            logger.error(f"Vector storage error: {str(e)}")
    
    async def search_similar(self, text: str, top_k: int = 5) -> List[dict]:
        try:
            if not self.index:
                logger.warning("Vector index not available")
                return []
            
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            response = client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            query_embedding = response.data[0].embedding
            results = self.index.query(query_embedding, top_k=top_k, include_metadata=True)
            return results.get("matches", [])
        except Exception as e:
            logger.error(f"Vector search error: {str(e)}")
            return []
