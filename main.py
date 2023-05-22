import tiktoken

from app import create_app

# print tiktoken version
print("tiktoken version: " + tiktoken.__version__)

app = create_app()
