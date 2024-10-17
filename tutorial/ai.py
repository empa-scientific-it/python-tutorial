import os


def config(api_key: str, model: str = "gpt-4o-mini", language: str = "English"):
    os.environ.update(
        {"OPENAI_API_KEY": api_key, "OPENAI_MODEL": model, "OPENAI_LANGUAGE": language}
    )
