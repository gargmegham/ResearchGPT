## ResearchGPT

An AI assistant to help you with with your research on various topics with abstract feed which is fetched from PubMed API on PubTrawlr platform

---

## Installation

1. Install poetry

2. Install python version >= 3.11.1

3. Install dependencies `poetry install`

4. Create .env file from example `cp config/.env.example config/.env`

5. Visit openai to obtain your [API key](https://platform.openai.com/account/api-keys) and then place it after `OPENAI_API_KEY=` in config.ini

---

## Local Server

- Use VSCode run and debug play button, repo include .vscode/launch.json file
- You should see the below sample stdout

```
INFO:     Started server process [20149]
INFO:     Waiting for application startup.
[2023-05-17 15:03:21,196] FastAPI:CRITICAL - MySQL DB connected!
[2023-05-17 15:03:22,103] FastAPI:CRITICAL - Redis CACHE connected!
INFO:     Application startup complete.
```

---

### You can use `curl http://127.0.0.1:8000` to check if the server is running or not, you'll get {"message":"Server is running..."} in response

---

## Prod Server

- `sudo docker-compose --env-file config/.env up -d`
- `sudo docker-compose --env-file config/.env down && sudo docker system prune --force --all`

---
