import logging
import traceback
import typing as t
from enum import Enum
from threading import Timer

import ipywidgets as widgets
import markdown2 as md
import openai
from IPython.display import Code, display, display_html
from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageParam,
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

    def change_model(self, model: str) -> None:
        """Change the active OpenAI model in use"""
        if model not in GPT_ALL_MODELS:
            raise ValueError(f"Unknown model: {model}")
        self.model = model
        logger.info("Model changed to %s", self.model)

    @retry(
        retry=retry_if_exception_type(openai.RateLimitError),
        stop=stop_after_attempt(3),
        wait=wait_fixed(10) + wait_random(0, 5),
    )
    def get_chat_response(
        self, query: str, *args, **kwargs
    ) -> ParsedChatCompletionMessage | ChatCompletionMessage:
        """Fetch a completion from the chat model"""
        system_prompt = (
            "As an expert Python developer, provide clear and concise explanations of error tracebacks, "
            "focusing on the root cause for users with minimal Python experience. "
            "Follow these guidelines strictly:\n"
            "- Offer hints, even for trivial errors.\n"
            "- Avoid providing exact solutions.\n"
            f"- Respond in {self.language}.\n"
            "- Any text or string must be written in Markdown."
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
            return response.choices[0].message


class ButtonState(Enum):
    """The state of the explanation button"""

    READY = "ready"
    LOADING = "loading"
    WAIT = "waiting"


class AIExplanation:
    """Class representing an AI-generated explanation"""

    def __init__(
        self,
        ipytest_result: "IPytestResult",
        exception: BaseException,
        openai_client: "OpenAIWrapper",
        wait_time: int = 60,  # Wait time in seconds
    ) -> None:
        """Public constructor for an explanation widget"""
        self.ipytest_result = ipytest_result
        self.exception = exception
        self.openai_client = openai_client

        # The output widget for displaying the explanation
        self._output = widgets.Output()

        # Timer and state
        self._timer: t.Optional[Timer] = None
        self._is_throttled = False
        self._wait_time = float(wait_time)
        self._remaining_time = float(wait_time)

        # The button widget for fetching the explanation
        self._button_styles = {
            ButtonState.READY: {
                "description": "Get AI Explanation",
                "icon": "search",
                "disabled": False,
            },
            ButtonState.LOADING: {
                "description": "Loading...",
                "icon": "spinner",
                "disabled": True,
            },
            ButtonState.WAIT: {
                "description": "Wait {seconds} seconds",
                "icon": "hourglass-start",
                "disabled": True,
            },
        }
        self._current_state = ButtonState.READY
        self._button = widgets.Button()
        self._update_button_state(ButtonState.READY)
        self._button.on_click(self._handle_click)
        self._button.observe(self._handle_state_change, names=["disabled"])

        # Set a default query
        self._query = (
            "I wrote the following Python function:\n\n"
            "{function_code}\n\n"
            "Whose docstring describes the purpose, arguments, and expected return values:\n\n"
            "{docstring}\n\n"
            "Running pytest on this function failed, and here is the error traceback I encountered:\n\n"
            "{traceback}"
        )

    @property
    def output(self) -> t.Tuple[widgets.Button, widgets.Output]:
        """Return the button and output widget as a tuple"""
        return self._button, self._output

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
        if (
            "{function_code}" not in q
            or "{traceback}" not in q
            or "{docstring}" not in q
        ):
            logger.error(
                "Query must contain placeholders: {function_code}, {docstring}, {traceback}"
            )
            raise ValueError
        self._query = q

    def _update_remaining_time(self):
        """Update the button label with remaining time"""
        self._remaining_time = max(0, self._remaining_time - 1)
        if self._is_throttled:
            self._update_button_state(ButtonState.WAIT)

    def _update_button_state(self, state: ButtonState) -> None:
        """Update the button state"""
        self._current_state = state
        style = self._button_styles[state].copy()

        if state == ButtonState.WAIT:
            style["description"] = style["description"].format(
                seconds=int(self._remaining_time)
            )

        self._button.description = style["description"]
        self._button.icon = style["icon"]
        self._button.disabled = style["disabled"]

    def _handle_state_change(self, change):
        """Handle the state change of the button"""
        if change["new"]:
            if self._is_throttled:
                self._update_button_state(ButtonState.WAIT)
        else:
            self._is_throttled = False
            self._update_button_state(ButtonState.READY)

    def _enable_button(self):
        """Enable the button after a delay"""
        self._button.disabled = False
        self._timer = None
        self._remaining_time = self._wait_time

    def _handle_click(self, _) -> None:
        """Handle the button click event with throttling"""
        if self._is_throttled:
            self._update_button_state(ButtonState.WAIT)
            return

        self._is_throttled = True
        self._button.disabled = True
        self._remaining_time = self._wait_time

        def update_timer():
            if self._remaining_time > 0:
                self._update_remaining_time()
                self._timer = Timer(1, update_timer)
                self._timer.start()
            else:
                self._enable_button()

        self._timer = Timer(1.0, update_timer)
        self._timer.start()

        # Call the method to fetch the explanation
        self._fetch_explanation()

    def _fetch_explanation(self) -> None:
        """Fetch the explanation from OpenAI API"""
        logger.debug("Attempting to fetch explanation from OpenAI API.")

        if not self.openai_client:
            return

        self._update_button_state(ButtonState.LOADING)

        traceback_str = "".join(traceback.format_exception_only(self.exception))
        logger.debug("Formatted traceback: %s", traceback_str)

        with self._output:
            self._output.clear_output()

            try:
                assert self.ipytest_result.function is not None

                query = self._query.format(
                    function_code=self.ipytest_result.function.source_code,
                    docstring=self.ipytest_result.function.implementation.__doc__,
                    traceback=traceback_str,
                )
                response = self.openai_client.get_chat_response(
                    query,
                    temperature=0.2,
                )

                logger.debug("Received response: %s", response)

                formatted_response = self._format_explanation(response)

                logger.debug("Formatted response: %s", formatted_response)

                if formatted_response:
                    display(widgets.VBox(children=formatted_response))
                else:
                    display_html(
                        "<p>No explanation could be generated for this error.</p>",
                        raw=True,
                    )
            except Exception as e:
                logger.exception("An error occurred while fetching the explanation.")
                display_html(f"<p>Failed to fetch explanation: {e}</p>", raw=True)
            finally:
                if self._is_throttled:
                    self._update_button_state(ButtonState.WAIT)
                else:
                    self._update_button_state(ButtonState.READY)

    def _format_explanation(
        self, chat_response: ParsedChatCompletionMessage | ChatCompletionMessage
    ) -> t.Optional[t.List[t.Any]]:
        """Format the explanation response for display"""

        # Initialize the Markdown to HTML converter
        def to_html(text: t.Any) -> str:
            """Markdown to HTML converter"""
            return md.markdown(str(text))

        if (
            isinstance(chat_response, ParsedChatCompletionMessage)
            and (explanation := chat_response.parsed) is not None
        ):
            logger.debug("Response is a valid `Explanation` object that can be parsed.")

            # A list to store all the widgets
            widgets_list = []

            # A summary of the explanation
            summary_widget = widgets.HTML(f"<h3>{to_html(explanation.summary)}</h3>")
            widgets_list.append(summary_widget)

            # Add steps as Accordion widgets
            steps_widgets = []
            for i, step in enumerate(explanation.steps, start=1):
                step_title = step.title or f"Step {i}"
                step_content = widgets.HTML(to_html(step.content))
                step_accordion = widgets.Accordion(
                    children=[step_content], titles=(step_title,)
                )
                steps_widgets.append(step_accordion)

            widgets_list.extend(steps_widgets)

            # Add code snippets using Code widgets
            if explanation.code_snippets:
                for i, snippet in enumerate(explanation.code_snippets, start=1):
                    snippet_output = widgets.Output()
                    snippet_description = widgets.HTML(to_html(snippet.description))
                    snippet_output.append_display_data(snippet_description)

                    snippet_code = Code(language="python", data=snippet.code)
                    snippet_output.append_display_data(snippet_code)

                    snippet_accordion = widgets.Accordion(
                        children=[snippet_output], titles=(f"Code Snippet #{i}",)
                    )

                    widgets_list.append(snippet_accordion)

            # Add hints as bullet points
            if explanation.hints:
                hints_html = (
                    "<ul>"
                    + "".join(f"<li>{to_html(hint)}</li>" for hint in explanation.hints)
                    + "</ul>"
                )
                hints_widget = widgets.Accordion(
                    children=[widgets.HTML(hints_html)],
                    titles=("Hints",),
                )
                widgets_list.append(hints_widget)

            return widgets_list

        elif (
            isinstance(chat_response, ChatCompletionMessage)
            and (explanation := chat_response.content) is not None
        ):
            logger.debug(
                "Response is not a structured `Explanation` object, returning as-is."
            )
            explanation = (
                explanation.removeprefix("```html").removesuffix("```").strip()
            )
            return [widgets.HTML(to_html(explanation))]

        logger.debug("Failed to parse explanation.")

        return None
