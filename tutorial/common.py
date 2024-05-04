import random

import ipywidgets as ipw


class Question(ipw.VBox):
    def __init__(
        self,
        question: str,
        options: dict,
        correct_answer: str,
        hint: str = None,
        shuffle: bool = False,
        prepend_text="",
    ):
        """A Question widget.

        question: The question text.
        options: A dictionary of options.
        correct_answer: The correct answer.
        hint: A hint to be displayed when the help button is clicked.
        shuffle: Whether to shuffle the options.
        """
        self.correct_answer = correct_answer
        self.hint = hint
        self.question = ipw.HTML(question)
        # Shuffle options if requested.
        if shuffle:
            options = sorted(options.items(), key=lambda x: random.random())

        # Radio buttons with options.
        self.answer = ipw.RadioButtons(
            options=options, value=None, layout={"width": "max-content"}
        )
        self.answer.observe(self.clear_output, "value")

        # Help button
        self.help_button = ipw.Button(
            icon="fa-question",
            layout={
                "visibility": "visible" if self.hint else "hidden",
                "width": "30px",
            },
        )
        self.help_button.on_click(self.on_help_button_clicked)

        self.output = ipw.HTML()
        super().__init__(
            [self.question, self.answer, ipw.HBox([self.help_button, self.output])]
        )

    def verify(self):
        """Verifies the answer and displays the result. Returns True if the answer is correct, False otherwise."""
        if self.correct_answer_given():
            self.output.value = (
                f"""<p style="color:MediumSeaGreen;">{self.answer.value}</p>"""
            )
            return True
        else:
            self.output.value = f"""<p style="color:Tomato;">{self.answer.value}</p>"""
            return False

    def request_answer_if_necessary(self):
        if not self.answer_is_given():
            self.output.value = (
                """<p style="color:Tomato;">Please select an answer.</p>"""
            )

    def on_help_button_clicked(self, _):
        self.output.value = f"""<p style="color:RoyalBlue;">Hint: {self.hint}</p>"""

    def clear(self):
        self.answer.value = None
        self.clear_output()  # if the value above was already None, the output will not be cleared

    def clear_output(self, _=None):
        """Clears the output when the answer is changed."""
        self.output.value = ""

    def correct_answer_given(self):
        return self.answer.label == self.correct_answer

    def answer_is_given(self):
        return self.answer.value is not None


class Quiz(ipw.VBox):
    def __init__(self, questions: list = None) -> None:
        """A Quiz widget.

        questions: A list of Question widgets.
        """
        self.verify_button = ipw.Button(description="Verify", button_style="success")
        self.verify_button.on_click(self.verify)

        self.clear_button = ipw.Button(description="Clear", button_style="danger")
        self.clear_button.on_click(self.clear)

        self.output = ipw.HTML()

        self.aux = [ipw.HBox([self.verify_button, self.clear_button]), self.output]

        super().__init__()

        self.nquestions = 0
        self.questions = []
        for question in questions:
            self.add_question(question)

    def add_question(self, question: Question):
        """Adds a question to the quiz."""
        question.question.value = (
            f"""<strong>Q{self.nquestions + 1}:</strong> """ + question.question.value
        )
        self.questions.append(question)
        self.children = self.questions + self.aux
        self.nquestions += 1

    def questions_not_answered(self):
        """Returns a list of question numbers that are not answered."""
        to_return = []
        for i, question in enumerate(self.questions):
            if not question.answer_is_given():
                question.request_answer_if_necessary()
                to_return.append(i + 1)
        return to_return

    def erroneous_responses(self):
        """Returns a list of question numbers that are answered incorrectly."""
        to_return = []
        for i, question in enumerate(self.questions):
            if not question.verify():
                to_return.append(i + 1)
        return to_return

    def verify(self, _=None):
        """Verifies the answers and displays the results."""

        # Dealing with unanswered questions.
        not_answered = self.questions_not_answered()
        if not_answered:
            self.output.value = f"""<p style="color:Tomato;">You didn't answer the following questions: {", ".join(map(str, not_answered))}!</p>"""
            return

        # Dealing with erroneous responses.
        errors = self.erroneous_responses()
        if errors:
            self.output.value = f"""<p style="color:Tomato;">Your answers to the following questions are <strong>incorrect</strong>: {", ".join(map(str, errors))}!</p>"""
        else:
            self.output.value = """<p style="color:MediumSeaGreen;">All correct!</p>"""

    def clear(self, _=None):
        """Clears the answers."""
        for question in self.questions:
            question.clear()
        self.output.value = ""


class Spoiler(ipw.Accordion):
    def __init__(self, title: str, content: str, show_content: bool = False):
        """A Spoiler widget.

        title: The title of the spoiler.
        content: The content of the spoiler.
        open: Whether the spoiler is open or closed.
        """
        super().__init__()
        self.children = [ipw.HTML(content)]
        self.set_title(0, title)
        self.selected_index = 0 if show_content else None
