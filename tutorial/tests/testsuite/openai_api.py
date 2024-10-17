import logging
import typing as t
from functools import lru_cache

import openai
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
    wait_random,
)

# Set logger
logger = logging.getLogger(__name__)

# OpenAI models
GPT_STABLE_MODELS = ("gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-4o-mini")
GPT_ALL_MODELS = GPT_STABLE_MODELS

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_LANGUAGE = "English"


class OpenAIWrapper:
    """A simple API wrapper adapted for IPython environments"""

    def __init__(
        self,
        api_key: str,
        model: t.Optional[str] = None,
        language: t.Optional[str] = None,
    ) -> None:
        """Initialize the wrapper for OpenAI API with logging and checks"""
        self.api_key = api_key
        self.model = model or DEFAULT_MODEL
        self.language = language or DEFAULT_LANGUAGE
        self.client = openai.OpenAI(api_key=self.api_key)

        if model not in GPT_ALL_MODELS:
            raise ValueError(
                f"Invalid model: {model}. Available models: {GPT_ALL_MODELS}"
            )

    def change_model(self, model: str) -> None:
        """Change the active OpenAI model in use"""
        if model not in GPT_ALL_MODELS:
            raise ValueError(f"Unknown model: {model}")
        self.model = model
        logger.info(f"Model changed to {self.model}")

    @lru_cache
    @retry(
        retry=retry_if_exception_type(openai.RateLimitError),
        stop=stop_after_attempt(3),
        wait=wait_fixed(10) + wait_random(0, 5),
    )
    def get_chat_response(self, query: str) -> ChatCompletion:
        """Fetch a completion from the chat model"""
        system_prompt = (
            "You are an expert Python developer tasked with explaining error tracebacks "
            "in a clear and concise manner. Your explanations should be easy to understand, "
            "highlighting the root cause of the error. "
            "The average user is likely to have very little experience with Python. "
            "Instructions:\n\n"
            " - Even if the error is trivial, provide some hints.\n"
            " - Refrain from writing an exact solution to the problem.\n"
            " - The output must be formatted in HTML as it will displayed inside a Jupyter notebook.\n"
            f" - Write your response in {self.language}."
        )

        messages: t.List[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages
            )
        except openai.APIError as e:
            logger.exception(f"API error: {e}")
            raise
        else:
            return response
