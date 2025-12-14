import httpx
from typing import Dict, Any, Optional

class RAGClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def search(
        self,
        query: str,
        author: Optional[str] = None,
        date: Optional[str] = None,
        topic: Optional[str] = None
    ) -> Dict[str, Any]:
        filters = {}
        if author:
            filters["author"] = author
        if date:
            filters["date"] = date
        if topic:
            filters["topic"] = topic

        payload = {"query": query, "filters": filters}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise Exception(f"Ошибка при вызове RAG API: {e}")