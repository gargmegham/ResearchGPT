import base64
from asyncio import gather
from datetime import datetime

from langchain.docstore.document import Document
from langchain.text_splitter import TokenTextSplitter

from database import cache


class VectorStoreManager:
    """
    VectorStoreManager
    =================
    A brief explanation of the VectorStoreManager class:
        - create_documents: Create documents from text and add them to the vectorstore.
        - asimilarity_search: Perform approximate similarity search on the vectorstore.
    A document is a string of text that is tokenized and embedded into a vector.
    A vector is a list of floats that represents a document.
    The vectorstore is a database of vectors that can be searched for approximate similarity.
    Vectorization is the process of converting a document into a vector.
    """

    @staticmethod
    async def create_documents(
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 0,
        tokenizer_model: str = "gpt-3.5-turbo",
        search: str = None,
    ) -> list[str]:
        """Create documents from text and add them to the vectorstore."""
        texts = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            model_name=tokenizer_model,
        ).split_text(text)
        if search:
            base64_search = base64.b64encode(search.encode("utf-8")).decode("utf-8")
            redis_key = f"doc:search:{base64_search}"
            timestamp = str(datetime.now().timestamp())
            old_timestamp = await cache.redis.get(redis_key)
            if not old_timestamp:
                await cache.redis.set(redis_key, timestamp)
            elif float(timestamp) - float(old_timestamp) > 604800:
                await cache.redis.set(redis_key, timestamp)
                return texts
            else:
                return texts
        await cache.vectorstore.aadd_texts(texts=texts)
        return texts

    @staticmethod
    async def asimilarity_search(
        queries: list[str], k: int = 1
    ) -> list[list[Document]]:
        """Perform approximate similarity search on the vectorstore."""
        return await gather(
            *[cache.vectorstore.asimilarity_search(query, k=k) for query in queries]
        )
