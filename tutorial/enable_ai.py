import os


def set_key(api_key: str):
    os.environ["OPENAI_API_KEY"] = api_key
