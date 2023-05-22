from app import create_app
import tiktoken

# print tiktoken version
print("tiktoken version: " + tiktoken.__version__)

app = create_app()
