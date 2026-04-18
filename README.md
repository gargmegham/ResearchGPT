# ResearchGPT

An AI-powered research assistant that lets you create persistent chat sessions, upload documents, and query GPT models in real time. Built with FastAPI, Svelte, MySQL, and Redis.

---

## UI Screenshots

<table>
  <tr>
    <td><img src="https://github.com/gargmegham/ResearchGPT/assets/95271253/d28187c2-959b-4671-b27c-93a94ede20f5" alt="loaded state"></td>
    <td><img src="https://github.com/gargmegham/ResearchGPT/assets/95271253/e7efbbda-e39a-45c8-a541-925fd8211d67" alt="loading state"></td>
  </tr>
  <tr>
    <td><img src="https://github.com/gargmegham/ResearchGPT/assets/95271253/6e3bbe63-bc4c-44c4-898c-e52d3bbddd59" alt="mobile-main"></td>
    <td><img src="https://github.com/gargmegham/ResearchGPT/assets/95271253/62fdfdd0-f875-4d5a-bcb6-0e893c9c37e3" alt="mobile-sidebar"></td>
  </tr>
</table>

---

## Features

- **Persistent chatrooms** — create, rename, and delete research sessions; history is saved per user
- **Streaming responses** — real-time token streaming over WebSocket
- **Document upload** — attach PDFs, text files, and images (OCR via Tesseract); content is chunked and embedded into a vector store for semantic retrieval
- **Multiple LLM backends** — OpenAI GPT-3.5/GPT-4 by default; local Llama models supported via llama-cpp-python
- **Research visualizations** — topic graphs (UMAP), bar/line charts, word clouds, network graphs, and article/author/journal views
- **Command system** — messages beginning with `/` trigger special handlers
- **JWT authentication** — token-based auth with AES-256-CBC encryption on sensitive data
- **Token usage limits** — per-request token caps to control API costs

---

## Architecture

```
ResearchGPT/
├── server/          # Python / FastAPI backend
│   ├── app/         # HTTP routes, WebSocket endpoint, middleware, auth
│   ├── database/    # SQLAlchemy (MySQL) models, Redis client, repository layer
│   ├── gpt/         # LLM integration, streaming, document embeddings, commands
│   ├── nginx/       # Reverse-proxy config and Dockerfile
│   ├── main.py      # Application entry point
│   ├── docker-compose.yaml
│   └── pyproject.toml
└── client/          # Svelte / TypeScript frontend
    └── src/
        ├── lib/pages/       # Home and Assistant pages
        ├── lib/components/  # Chat UI, message display, visualizations
        ├── lib/views/       # Articles, Journals, Authors, Resources
        └── lib/apis/        # HTTP + WebSocket API calls
```

**Backend services (via Docker Compose)**

| Service | Role | Port |
|---------|------|------|
| `api` | FastAPI HTTP server | 8000 |
| `ws` | FastAPI WebSocket worker | 8001 |
| `web` | Nginx reverse proxy + SSL | 80 / 443 |
| `database` | MySQL | 3306 |
| `cache` | Redis (session cache + vector store) | 6379 |
| `certbot` | Let's Encrypt certificate renewal | — |

HTTP traffic routes to `api`; WebSocket connections (`/ws/`) route to the dedicated `ws` worker.

---

## Tech Stack

**Server**
- Python 3.11+, FastAPI, Uvicorn / Gunicorn
- SQLAlchemy 2 (async) + aiomysql
- Redis + LangChain vector store (embeddings)
- OpenAI API; llama-cpp-python for local models
- PyJWT, cryptography (AES-256-CBC)
- pdf2image, pytesseract, unstructured (document parsing)
- tiktoken (token counting)

**Client**
- Svelte 3 + SvelteKit, TypeScript, Vite
- Tailwind CSS
- Lucide Svelte icons
- vis-network (graph visualizations)

---

## Server Setup

### Prerequisites

- Python 3.11.1+
- [Poetry](https://python-poetry.org/docs/#installation)
- MySQL and Redis instances (or use Docker Compose for everything)
- An [OpenAI API key](https://platform.openai.com/account/api-keys)

### Install dependencies

```bash
cd server
poetry install
```

### Configure environment

```bash
cp config/.env.example config/.env
```

Edit `config/.env` and fill in at minimum:

```env
OPENAI_API_KEY=sk-...
JWT_SECRET=<random secret>
MYSQL_HOST=localhost
MYSQL_USER=admin
MYSQL_PASSWORD=...
MYSQL_DATABASE=researchgpt
REDIS_HOST=localhost
REDIS_PASSWORD=...
```

### Run locally

Use the VSCode **Run and Debug** panel (a `launch.json` is included). On successful startup you should see:

```
INFO: Started server process [...]
INFO: Waiting for application startup.
FastAPI:CRITICAL - MySQL DB connected!
FastAPI:CRITICAL - Redis CACHE connected!
INFO: Application startup complete.
```

Verify with:

```bash
curl http://127.0.0.1:8000
# {"message":"Server is running..."}
```

### Deploy to production (Docker)

```bash
# Issue SSL certificates
sudo chmod +x server/certbot.sh && sudo ./server/certbot.sh

# Start all services
sudo docker-compose --env-file server/config/.env up -d --build --remove-orphans

# View logs
sudo docker exec -it researchgpt_api_1 cat log/app.log

# Tear down and clean up
sudo docker-compose --env-file server/config/.env down && sudo docker system prune --force --all
```

Set `CERTBOT_EMAIL` and `CERTBOT_DOMAIN` in your `.env` before running certbot.

---

## Client Setup

### Prerequisites

- Node.js (v18+ recommended)

### Install and run

```bash
cd client
npm install
npm run dev       # dev server at http://localhost:8080
```

### Build for production

```bash
npm run build     # output in dist/
```

Other scripts: `npm run lint`, `npm run check`, `npm run format`.

---

## Environment Variables Reference

| Variable | Description |
|----------|-------------|
| `HOST_MAIN` | Allowed CORS origin (your frontend URL) |
| `DEBUG_MODE` | `1` for debug logging, `0` for production |
| `JWT_SECRET` | Secret used to sign JWTs |
| `OPENAI_API_KEY` | OpenAI API key |
| `DEFAULT_LLM_MODEL` | `gpt_4` or `gpt_3_5_turbo` |
| `MYSQL_HOST` | MySQL hostname |
| `MYSQL_USER` | MySQL username |
| `MYSQL_PASSWORD` | MySQL password |
| `MYSQL_PORT` | MySQL port (default `3306`) |
| `MYSQL_DATABASE` | Database name |
| `REDIS_HOST` | Redis hostname |
| `REDIS_PORT` | Redis port (default `6379`) |
| `REDIS_DB` | Redis database index |
| `REDIS_PASSWORD` | Redis password |
| `REDIS_USER` | Redis username (default `default`) |
| `CERTBOT_EMAIL` | Email for Let's Encrypt registration |
| `CERTBOT_DOMAIN` | Domain for SSL certificate |

See `server/config/.env.example` for the full template.
