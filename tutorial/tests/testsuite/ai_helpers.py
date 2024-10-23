import logging
import traceback
import typing as t

import ipywidgets as widgets
import markdown2 as md
import openai
from IPython.display import display_html
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ParsedChatCompletion,
    ParsedChatCompletionMessage,
)
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
    wait_random,
)

if t.TYPE_CHECKING:
    from .helpers import IPytestResult

# Set logger
logger = logging.getLogger()

# OpenAI models
GPT_STABLE_MODELS = ("gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-4o-mini")
GPT_ALL_MODELS = GPT_STABLE_MODELS

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_LANGUAGE = "English"


class ExplanationStep(BaseModel):
    """A single step in the explanation"""

    title: t.Optional[str]
    content: str


class CodeSnippet(BaseModel):
    """A code snippet with optional description"""

    code: str
    description: t.Optional[str]


class Explanation(BaseModel):
    """A structured explanation with steps, code snippets, and hints"""

    summary: str
    steps: t.List[ExplanationStep]
    code_snippets: t.List[CodeSnippet]
    hints: t.List[str]


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

        if self.model not in GPT_ALL_MODELS:
            raise ValueError(
                f"Invalid model: {model}. Available models: {GPT_ALL_MODELS}"
            )

        self._cache = {}

    def change_model(self, model: str) -> None:
        """Change the active OpenAI model in use"""
        if model not in GPT_ALL_MODELS:
            raise ValueError(f"Unknown model: {model}")
        self.model = model
        logger.info("Model changed to %s", self.model)

    def get_chat_response(
        self, query: str, *args, **kwargs
    ) -> ParsedChatCompletion | ChatCompletion:
        """Get a (cached) chat response from the OpenAI API"""
        cache_key = self._cache_key(query)

        if cache_key in self._cache:
            return self._cache[cache_key]

        response = self._get_chat_response(query, *args, **kwargs)
        self._cache[cache_key] = response

        return response

    def _cache_key(self, query: str) -> str:
        """Generate a unique cache key for a query, model, and language"""
        return f"{self.model}:{self.language}:{query}"

    @retry(
        retry=retry_if_exception_type(openai.RateLimitError),
        stop=stop_after_attempt(3),
        wait=wait_fixed(10) + wait_random(0, 5),
    )
    def _get_chat_response(
        self, query: str, *args, **kwargs
    ) -> ParsedChatCompletion | ChatCompletion:
        """Fetch a completion from the chat model"""
        system_prompt = (
            "As an expert Python developer, provide clear and concise explanations of error tracebacks, "
            "focusing on the root cause for users with minimal Python experience. "
            "Follow these guidelines strictly:\n"
            "- Offer hints, even for trivial errors.\n"
            "- Avoid providing exact solutions.\n"
            f"- Respond in {self.language}."
        )

        messages: t.List[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        try:
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=Explanation,
                **kwargs,
            )
        except openai.APIError:
            logger.exception("API error encountered.")
            raise
        except openai.LengthFinishReasonError:
            logger.exception("Input prompt has too many tokens.")
            raise
        else:
            return response


class AIExplanation:
    """Class representing an AI-generated explanation"""

    def __init__(
        self,
        ipytest_result: "IPytestResult",
        exception: BaseException,
        openai_client: "OpenAIWrapper",
    ) -> None:
        """Initialize the explanation object"""
        self.ipytest_result = ipytest_result
        self.exception = exception
        self.openai_client = openai_client

        self._button = widgets.Button(description="Get AI Explanation", icon="search")
        self._output = widgets.Output()
        self._button.on_click(self._fetch_explanation)
        # Set a default query
        self._query = (
            "I wrote the following Python function:\n\n"
            "{function_code}\n\n"
            "Here is the error traceback I encountered:\n\n"
            "{traceback}"
        )

    @property
    def query(self) -> str:
        """Return the query for the AI explanation"""
        return self._query

    @query.setter
    def query(self, q: str) -> None:
        """Set the query for the AI explanation"""
        if not q:
            logger.error("Query cannot be empty.")
            raise ValueError
        if "{function_code}" not in q or "{traceback}" not in q:
            logger.error(
                "Query must contain placeholders: {function_code}, {traceback}"
            )
            raise ValueError
        self._query = q

    def _fetch_explanation(self, _) -> None:
        """Fetch the explanation from OpenAI API"""
        logger.debug("Attempting to fetch explanation from OpenAI API.")

        if not self.openai_client:
            return

        self._button.description = "Loading..."
        self._button.icon = "spinner"

        traceback_str = "".join(traceback.format_exception_only(self.exception))
        logger.debug("Formatted traceback: %s", traceback_str)

        with self._output:
            self._output.clear_output()

            try:
                # TODO: allow using a custom query
                response = self.openai_client.get_chat_response(
                    "I wrote the following Python function:\n\n"
                    f"{self.ipytest_result.function_code}\n\n"
                    "Here is the error traceback I encountered:\n\n"
                    f"{traceback_str}",
                    temperature=0.2,
                )

                logger.debug("Received response: %s", response)

                formatted_response = self._format_explanation(response)

                logger.debug("Formatted response: %s", formatted_response)

                if formatted_response:
                    display_html(str(formatted_response), raw=True)
                else:
                    display_html(
                        "<p>No explanation could be generated for this error.</p>",
                        raw=True,
                    )
            except Exception as e:
                logger.exception("An error occurred while fetching the explanation.")
                display_html(f"<p>Failed to fetch explanation: {e}</p>", raw=True)
            finally:
                self._button.description = "Get AI Explanation"
                self._button.icon = "search"

    def _format_explanation(
        self, chat_response: ParsedChatCompletion[Explanation] | ChatCompletion
    ) -> t.Optional[str]:
        """Format the explanation response for display"""

        # Initialize the Markdown > HTML converter
        def to_html(text: t.Any) -> str:
            return md.markdown(str(text))

        explanation_response = chat_response.choices[0].message

        if isinstance(explanation_response, ParsedChatCompletionMessage) and (
            explanation := explanation_response.parsed
        ):
            logger.debug("Response is a valid `Explanation` object that can be parsed.")

            # Format the summary as an <h3> heading
            html_output = f"<h3>{to_html(explanation.summary)}</h3>"

            # Add steps as paragraphs
            for step in explanation.steps:
                if step.title:
                    # If the step has a title, use this as a subheading
                    html_output += f"<h4>{to_html(step.title)}</h4>"
                html_output += f"{to_html(step.content)}"

            # Add code snippets within <pre><code> tags
            if explanation.code_snippets:
                html_output += "<h4>Code Snippets:</h4>"
                for snippet in explanation.code_snippets:
                    if snippet.description:
                        html_output += to_html(f"**{snippet.description}**")
                    html_output += f"<div style='margin:8px 0;'><pre><code>{snippet.code}</code></pre></div>"

            # Add hints as bullet points
            if explanation.hints:
                html_output += "<h4>Hints:</h4>"
                html_output += "<ul>"
                for hint in explanation.hints:
                    html_output += f"<li>{to_html(hint)}</li>"
                html_output += "</ul>"

            return html_output
        elif isinstance(explanation_response, ChatCompletionMessage) and (
            explanation := explanation_response.content
        ):
            logger.debug(
                "Response is not a structured `Explanation` object, returning as-is."
            )
            explanation = (
                explanation.removeprefix("```html").removesuffix("```").strip()
            )
            return explanation

        logger.debug("Failed to parse explanation.")
        return None

    @property
    def output(self) -> t.Tuple[widgets.Button, widgets.Output]:
        """Return the button and output widgets as a tuple"""
        return self._button, self._output
