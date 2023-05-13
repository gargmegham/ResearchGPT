## ResearchGPT

An AI assistant to help you with your research on various topics with data from PubMed API

## System Requirement

Tested on `MacOS` and `Ubuntu20 LTS`

Python version `>= python3.11.1`

## Installation

1. Install poetry

```
cd $PROJECT_ROOT
poetry install
```

## Start Server

Visit openai to obtain your [API key](https://platform.openai.com/account/api-keys) and [Organization ID](https://platform.openai.com/account/org-settings)

Then export to confi.ini file use config.ini.example for reference

```
cp config/config.ini.example config/config.ini
```

You should see the below sample stdout

```
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
ResearchGPT launched
--------------------------
```

Note that this server is detached from your terminal, you're free to close the terminal without interrupting the service.

Now, open web browser and visit http://0.0.0.0:8000. Enjoy
