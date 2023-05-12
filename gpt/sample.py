# %%
import logging
import os
import sys

from gpt_index import (GPTListIndex, GPTSimpleVectorIndex, LLMPredictor,
                       PromptHelper, SimpleDirectoryReader)
from langchain import OpenAI

logger = logging.getLogger(__name__)
# %%
# Open AI API Key
os.environ["OPENAI_API_KEY"] = "YOUR-OPENAI-KEY"


# %%
def createVectorIndex(path):
    max_input = 4096
    tokens = 200
    chunk_size = 600  # for LLM, we need to define chunk size
    max_chunk_overlap = 20

    promptHelper = PromptHelper(
        max_input, tokens, max_chunk_overlap, chunk_size_limit=chunk_size
    )  # define prompt

    llmPredictor = LLMPredictor(
        llm=OpenAI(temperature=0, model_name="text-ada-001", max_tokens=tokens)
    )  # define LLM ref: https://platform.openai.com/docs/models/gpt-3
    docs = SimpleDirectoryReader(path).load_data()  # load data

    vectorIndex = GPTSimpleVectorIndex(
        documents=docs, llm_predictor=llmPredictor, prompt_helper=promptHelper
    )  # create vector index

    vectorIndex.save_to_disk("vectorIndex.json")
    return vectorIndex


# %%
vectorIndex = createVectorIndex("dataset")


# %%
def queryGPT(vectorIndex):
    vIndex = GPTSimpleVectorIndex.load_from_disk(vectorIndex)
    while True:
        prompt = input("Please enter your query: ")
        response = vIndex.query(prompt, response_mode="compact")
        print(f"You Asked: {prompt} \n")
        print(f"GPT Response: {response} \n")


# %%
queryGPT("./vectorIndex.json")
