import json
from datetime import datetime

import requests

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


async def login(
    email: str = "meghamgarg@gmail.com", password: str = "Pubtrawlr.megham3@"
) -> str:
    with requests.session() as session:
        url = "https://app.synthbot.mindstaging.com/api/token"
        payload = json.dumps({"email": email, "password": password})
        headers = {"Content-Type": "application/json"}
        response = session.request("POST", url, headers=headers, data=payload)
        return json.loads(response.text)["token"]


async def pubmed_context(chatroom_id: int):
    chatroom = await repository.get_chatroom(chatroom_id)
    token = await login()
    search_term = chatroom.title
    search_id = chatroom.search
    with requests.session() as session:
        url = f"https://app.synthbot.mindstaging.com/api/abstracts/{search_id}"
        payload = {}
        headers = {"Authorization": f"Bearer {token}"}
        response = session.request("GET", url, headers=headers, data=payload)
        response_json = json.loads(response.text)
        processed_paper_text = process_papers(papers=response_json)
        if processed_paper_text:
            await VectorStoreManager.create_documents(
                processed_paper_text, search_term=search_term
            )
