from asyncio import gather

from langchain.docstore.document import Document
from langchain.text_splitter import TokenTextSplitter

from database import cache


class VectorStoreManager:
    @staticmethod
    async def create_documents(
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 0,
        tokenizer_model: str = "gpt-3.5-turbo",
    ) -> list[str]:
        texts = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            model_name=tokenizer_model,
        ).split_text(text)
        await cache.vectorstore.aadd_texts(texts=texts)
        return texts

    @staticmethod
    async def asimilarity_search(
        queries: list[str], k: int = 1
    ) -> list[list[Document]]:
        return await gather(
            *[cache.vectorstore.asimilarity_search(query, k=k) for query in queries]
        )
