import json

import requests

from app.globals import SECRET_KEY
from app.logger import api_logger
from database import repository, schemas
from gpt.vectorstore_manager import VectorStoreManager


def process_papers(papers: list[dict]) -> str:
    try:
        result = ""
        for paper in papers:
            schemas.PubMedPaper.validate(schemas.PubMedPaper(**paper))
            result += f"Title: {paper.get('title', '')} ::: {paper.get('pmid', '')}\n"
            result += f"Abstract: {paper.get('abstract', '')}\n"
            result += f"Authors: {paper.get('authors', '')}\n\n"
        return result
    except Exception as e:
        api_logger.error(f"Error processing papers: {e}")
        return None


async def pubmed_context(chatroom_id: int) -> None:
    try:
        chatroom = await repository.get_chatroom(chatroom_id)
        search_term = chatroom.title
        search_id = chatroom.search
        with requests.session() as session:
            url = f"https://app.synthbot.mindstaging.com/v2/abstracts/{search_id}"
            payload = {}
            headers = {"X-PubTrawlr-Microservice-Id": SECRET_KEY}
            response = session.request("GET", url, headers=headers, data=payload)
            response_json = json.loads(response.text)
            processed_paper_text = process_papers(papers=response_json)
            if processed_paper_text:
                await VectorStoreManager.create_documents(
                    processed_paper_text, search_term=search_term
                )
    except Exception as err:
        api_logger.error(f"Error in pubmed_context: {err}")
