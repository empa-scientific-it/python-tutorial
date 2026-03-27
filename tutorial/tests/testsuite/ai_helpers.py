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

from .exceptions import (
    APIConnectionError,
    InvalidAPIKeyError,
    InvalidModelError,
    UnexpectedAPIError,
    ValidationResult,
)

if t.TYPE_CHECKING:
    from .helpers import IPytestResult

# Set logger
logger = logging.getLogger()


class ExplanationStep(BaseModel):
    """A single step in the explanation"""

    title: str | None
    content: str


class CodeSnippet(BaseModel):
    """A code snippet with optional description"""

    code: str
    description: str | None


class Explanation(BaseModel):
    """A structured explanation with steps, code snippets, and hints"""

    summary: str
    steps: list[ExplanationStep]
    code_snippets: list[CodeSnippet]
    hints: list[str]


class OpenAIWrapper:
    """A simple API wrapper adapted for IPython environments"""

    # These are the models we can use: they must support structured responses
    GPT_MODELS = (
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4.1",
        "gpt-4.1-mini",
        "gpt-4.1-nano",
        "o4-mini",
    )

    DEFAULT_MODEL = "gpt-4o-mini"
    DEFAULT_LANGUAGE = "English"

    _instance = None

    def __new__(cls, *args, **kwargs) -> "OpenAIWrapper":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def create_validated(
        cls,
        api_key: str,
        model: str | None = None,
        language: str | None = None,
    ) -> tuple["OpenAIWrapper", ValidationResult]:
        instance = cls.__new__(cls)

        # Only initialize if not already
        if not hasattr(instance, "client"):
            instance.api_key = api_key
            instance.language = language or cls.DEFAULT_LANGUAGE
            instance.model = model or cls.DEFAULT_MODEL
            instance.client = openai.OpenAI(api_key=api_key)

        # Validate the model
        model_validation = instance.validate_model(instance.model)
        return instance, model_validation

    @classmethod
    def validate_api_key(cls, api_key: str | None) -> ValidationResult:
        """Validate the OpenAI API key"""
        if not api_key:
            return ValidationResult(
                is_valid=False,
                error=InvalidAPIKeyError("API key is missing."),
                message="OpenAI API key is not provided.",
            )

        try:
            client = openai.OpenAI(api_key=api_key)
            client.models.list()  # the simplest API call to verify the API
        except openai.AuthenticationError:
            return ValidationResult(
                is_valid=False,
                error=InvalidAPIKeyError("The provided API key is invalid."),
                message="Invalid OpenAI API key. Please, double check it.",
            )
        except openai.APIConnectionError:
            return ValidationResult(
                is_valid=False,
                error=APIConnectionError("Unable to connect to OpenAI."),
                message="Could not connect to OpenAI. Please, check your internet connection.",
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error=UnexpectedAPIError(f"Unexpected error: {e}"),
                message="An unexpected error occurred while validating API key.",
            )
        else:
            return ValidationResult(is_valid=True)

    def validate_model(self, model: str | None) -> ValidationResult:
        """Validate the model selection"""
        try:
            if model not in self.GPT_MODELS:
                return ValidationResult(
                    is_valid=False,
                    error=InvalidModelError(),
                    message=f"Invalid model: {model}. Available models: {' '.join(self.GPT_MODELS)}",
                )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error=UnexpectedAPIError(f"Error validating model: {e}"),
                message="Unexpected error during model validation",
            )

        return ValidationResult(is_valid=True)

    def __init__(
        self,
        api_key: str | None,
        model: str | None = None,
        language: str | None = None,
    ) -> None:
        """Initialize the wrapper for OpenAI API with logging and checks"""
        # Avoid reinitializing the client
        if hasattr(self, "client"):
            return

        # Validate the API key
        validation = self.validate_api_key(api_key)
        if not validation.is_valid:
            assert validation.error is not None  # for type checking
            raise validation.error

        self.api_key = api_key
        self.language = language or self.DEFAULT_LANGUAGE
        self.client = openai.OpenAI(api_key=self.api_key)

        self.model = model or self.DEFAULT_MODEL
        model_validation = self.validate_model(self.model)
        if not model_validation.is_valid:
            assert model_validation.error is not None  # type checking
            raise model_validation.error

    def change_model(self, model: str) -> None:
        """Change the active OpenAI model in use"""
        validation = self.validate_model(model)
        if not validation.is_valid:
            assert validation.error is not None  # type checking
            logger.exception("Error changing model")
            raise validation.error

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
            "- Take into account the number of attempts made by providing increasingly detailed hints after a failed attempt.\n"
            "- Do not provide verbatim solutions, only guidance.\n"
            f"- Respond in {self.language}.\n"
            "- Any text or string must be written in Markdown."
        )

        messages: list[ChatCompletionMessageParam] = [
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

    _STYLES = """
        <style>
            .ai-container {
                margin-top: 1.5rem;
                font-family: system-ui, -apple-system, sans-serif;
            }
            .ai-header {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                margin-bottom: 1rem;
            }
            .ai-title {
                font-size: 1.1rem;
                font-weight: 500;
            }
            .ai-button {
                background-color: #4b88ff;
                color: white;
                border: none;
                padding: 0;
                border-radius: 0.5rem;
                font-weight: 500;
                transition: all 0.2s ease;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                min-width: 200px;
                white-space: nowrap;
                text-overflow: ellipsis;
                overflow: hidden;
            }
            .ai-button:hover:not(:disabled) {
                background-color: #3b7bff;
                transform: translateY(-1px);
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
            }
            .ai-button:disabled {
                background-color: #94a3b8;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            .ai-timer {
                font-size: 0.9rem;
                color: #64748b;
                margin-left: 1rem;
                font-weight: 500;
            }
            .ai-content {
                margin-top: 1rem;
                border: 1px solid #e5e7eb;
                border-radius: 0.5rem;
                overflow: hidden;
            }
            .ai-explanation h3 {
                margin: 0 0 1rem 0;
                font-size: 1.1rem;
                color: #1f2937;
            }
            .ai-explanation .jupyter-widgets.accordion {
                margin: 0.75rem 0;
                border: 1px solid #e5e7eb;
                border-radius: 0.375rem;
                overflow: hidden;
            }
            .ai-explanation .jupyter-widgets.accordion > .accordion-header {
                background: #f9fafb;
                padding: 0.75rem 1rem;
                font-weight: 500;
            }
            .ai-explanation .jupyter-widgets.accordion > .accordion-content {
                padding: 1rem;
                background: white;
            }
            .ai-explanation code {
                background: #f3f4f6;
                padding: 0.2rem 0.4rem;
                border-radius: 0.25rem;
                font-size: 0.9em;
            }
            .ai-explanation pre {
                background: #f8f9fa;
                padding: 1rem;
                border-radius: 0.375rem;
                overflow-x: auto;
            }
        </style>
    """

    def __init__(
        self,
        ipytest_result: "IPytestResult",
        openai_client: "OpenAIWrapper",
        exception: BaseException | None = None,
        wait_time: int = 60,  # Wait time in seconds
    ) -> None:
        """Public constructor for an explanation widget"""
        self.ipytest_result = ipytest_result
        self.exception = exception
        self.openai_client = openai_client

        # The output widget for displaying the explanation
        self._output = widgets.Output()

        # Timer and state
        self._timer: Timer | None = None
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
                "description": "Please wait",
                "icon": "hourglass-start",
                "disabled": True,
            },
        }

        # Set a default query
        self._query_template = (
            "I wrote the following Python function:\n\n"
            "{function_code}\n\n"
            "Whose docstring describes the purpose, arguments, and expected return values:\n\n"
            "{docstring}\n\n"
            "Running pytest on this function failed, and here is the error traceback I got:\n\n"
            "{traceback}\n\n"
            "Consider that this is my {attempt_number} attempt."
        )

        # Default query params
        self._query_params = {
            "function_code": "",
            "docstring": "",
            "traceback": "",
            "attempt_number": self.ipytest_result.test_attempts,
        }

        # Create a header with button and timer
        self._header = widgets.Box(
            layout=widgets.Layout(
                display="flex",
                align_items="center",
                margin="0 0 1rem 0",
            )
        )

        # Create a timer display
        self._timer_display = widgets.HTML(
            value="", layout=widgets.Layout(margin="0 0 0 0.75rem")
        )

        # Initialize the button
        self._current_state = ButtonState.READY
        self._button = widgets.Button()
        self._update_button_state(ButtonState.READY)
        self._button.on_click(self._handle_click)
        self._button.observe(self._handle_state_change, names=["disabled"])

    def render(self) -> widgets.Widget:
        """Return a single widget containing all the components"""
        style_html = widgets.HTML(self._STYLES)

        header_html = widgets.HTML(
            '<div class="ai-header">'
            '<span class="ai-title">🤖 Explain With AI</span>'
            "</div>"
        )

        button_container = widgets.Box(
            [
                self._button,
                self._timer_display,
            ],
            layout=widgets.Layout(display="flex", align_iterms="center"),
        )

        # Create the rendered container
        container = widgets.VBox(
            children=[
                style_html,
                header_html,
                button_container,
                self._output,
            ],
            layout=widgets.Layout(margin="1rem 0 0 0", padding="0"),
        )

        return container

    def set_query_template(self, template: str) -> None:
        """Set the query template"""
        self._query_template = template

    def query_params(self, *args, **kwargs: t.Any) -> None:
        """Add/update multiple query parameters"""
        self._query_params.update(kwargs)

    @property
    def query(self) -> str:
        """Generate the query string"""
        logger.debug("Building a query with parameters: %s", self._query_params)
        try:
            return self._query_template.format(**self._query_params)
        except KeyError as e:
            logger.exception("Missing key in query parameter")
            raise ValueError from e

    def _update_remaining_time(self):
        """Update the button label with remaining time"""
        self._remaining_time = max(0, self._remaining_time - 1)
        if self._is_throttled:
            self._update_button_state(ButtonState.WAIT)

    def _update_button_state(self, state: ButtonState) -> None:
        """Update the button state"""
        self._current_state = state
        style = self._button_styles[state].copy()

        # Update the timer display
        if state == ButtonState.WAIT:
            self._timer_display.value = (
                '<span class="ai-timer">Available in '
                f"{int(self._remaining_time)} "
                "seconds</span>"
            )
        else:
            self._timer_display.value = ""

        self._button.add_class("ai-button")
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
        from .helpers import IPytestOutcome

        logger.debug("Attempting to fetch explanation from OpenAI API.")

        if not self.openai_client:
            return

        self._update_button_state(ButtonState.LOADING)

        if self.exception:
            traceback_str = "".join(traceback.format_exception_only(self.exception))
            logger.debug("Formatted traceback: %s", traceback_str)
        else:
            traceback_str = "No traceback available."

        with self._output:
            self._output.clear_output()

            try:
                # assert self.ipytest_result.function is not None
                match self.ipytest_result.status:
                    case IPytestOutcome.FINISHED if (
                        self.ipytest_result.function is not None
                    ):
                        self.query_params(
                            function_code=self.ipytest_result.function.source_code,
                            docstring=self.ipytest_result.function.implementation.__doc__,
                            traceback=traceback_str,
                        )
                    case _:
                        self.query_params(
                            function_code=self.ipytest_result.cell_content,
                            docstring="(Find it in the function's definition above.)",
                            traceback=traceback_str,
                        )

                response = self.openai_client.get_chat_response(
                    self.query,
                    temperature=0.2,
                )

                logger.debug("Received response: %s", response)

                formatted_response = self._format_explanation(response)

                logger.debug("Formatted response: %s", formatted_response)

                if formatted_response:
                    display(widgets.VBox(children=formatted_response))
                else:
                    display(widgets.HTML("<p>No explanation could be generated.</p>"))
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
    ) -> list[t.Any] | None:
        """Format the explanation response for display"""

        # Initialize the Markdown to HTML converter
        def to_html(text: t.Any) -> str:
            """Markdown to HTML converter"""
            return md.markdown(str(text))

        # Reset the explanation object
        explanation = None

        # A list to store all the widgets
        widgets_list = []

        if (
            isinstance(chat_response, ParsedChatCompletionMessage)
            and (explanation := chat_response.parsed) is not None
        ):
            logger.debug("Response is a valid `Explanation` object that can be parsed.")

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

            widgets_list.append(widgets.HTML(to_html(explanation)))

        if explanation is not None:
            # Wrap everything in a styled container
            container = widgets.VBox(
                children=[widgets.HTML('<div class="ai-explanation">')]
                + widgets_list
                + [widgets.HTML("</div>")]
            )
            return [container]
        else:
            logger.debug("Failed to parse explanation.")

        return None
