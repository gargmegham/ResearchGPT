## ResearchGPT

An AI assistant to help you with with your research

---

## UI Screenshots

![loaded state](https://github.com/gargmegham/ResearchGPT/assets/95271253/d28187c2-959b-4671-b27c-93a94ede20f5)
![loading state](https://github.com/gargmegham/ResearchGPT/assets/95271253/e7efbbda-e39a-45c8-a541-925fd8211d67)
![mobile-main](https://github.com/gargmegham/ResearchGPT/assets/95271253/6e3bbe63-bc4c-44c4-898c-e52d3bbddd59)
![mobile-sidebar](https://github.com/gargmegham/ResearchGPT/assets/95271253/62fdfdd0-f875-4d5a-bcb6-0e893c9c37e3)

---

## Installation

1. Install poetry

2. Install python version >= 3.11.1

3. Install dependencies `poetry install`

4. Create .env file from example `cp config/.env.example config/.env`

5. Visit openai to obtain your [API key](https://platform.openai.com/account/api-keys) and then place it after `OPENAI_API_KEY=` in config/.env

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

- `sudo chmod +x certbot.sh && sudo ./certbot.sh`
- `sudo docker-compose --env-file config/.env up -d --build --remove-orphans`
- `sudo docker-compose --env-file config/.env down && sudo docker system prune --force --all`
- `sudo docker exec -it researchgpt_api_1 cat log/app.log`

---
