import ipywidgets as ipw
import random

class Question(ipw.VBox):
    
    def __init__(self, question: str, options: dict, correct_answer: str, hint: str = None, shuffle: bool = False):
        """A Question widget.

            question: The question text.
            options: A dictionary of options.
            correct_answer: The correct answer.
            hint: A hint to be displayed when the help button is clicked.
            shuffle: Whether to shuffle the options.
        """
        self.correct_answer = correct_answer
        if shuffle:
            options = sorted(options.items(), key=lambda x: random.random())

        self.answer = ipw.RadioButtons(options=options, value=None, description='Answer')
        self.button = ipw.Button(description='Help me!', layout={'visibility': 'visible' if hint else 'hidden'}, button_style='warning')
        def on_help_button_clicked(_):
            self.output.value = f"""<p style="color:RoyalBlue;">Hint: {hint}</p>"""
        self.button.on_click(on_help_button_clicked)
        self.output = ipw.HTML()
        super().__init__([ipw.HTML(question), self.answer, self.button, self.output])
    
    def verify(self):
        if not self.answer_is_given():
            self.output.value = f"""<p style="color:Tomato;">Please select an answer.</p>"""
            return
        if self.correct_answer_given():
            text = f"""<p style="color:MediumSeaGreen;">{self.answer.value}</p>"""
        else:
            text = f"""<p style="color:Tomato;">{self.answer.value}</p>"""
        self.output.value = text
    
    def clear(self):
        self.answer.value = None
        self.output.value = ''
    
    def correct_answer_given(self):
        return self.answer.label == self.correct_answer
    
    def answer_is_given(self):
        return self.answer.value is not None

class Quiz(ipw.VBox):
    def __init__(self, questions: list=None) -> None:
        self.questions = questions

        self.verify_button = ipw.Button(description='Verify')
        self.verify_button.on_click(self.verify)

        self.clear_button = ipw.Button(description='Clear')
        self.clear_button.on_click(self.clear)

        self.output = ipw.HTML()

        self.aux = [ipw.HBox([self.verify_button, self.clear_button]), self.output]

        super().__init__(children=self.questions + self.aux)
    
    def add_question(self, question: Question):
        self.children = self.questions + [question] + self.aux
    
    def all_answers_given(self):
        to_return = True
        for question in self.questions:
            if not question.answer_is_given():
                question.verify()  # Will request the user to select an answer.
                to_return = False
        return to_return

    def verify(self, _=None):
        if not self.all_answers_given():
            return
        for question in self.questions:
            question.verify()
    
    def clear(self, _=None):
        for question in self.questions:
            question.clear()


