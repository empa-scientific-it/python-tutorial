import ipywidgets as ipw
from IPython import  display
from typing import Dict, Any, Callable
import inspect
from IPython.core.interactiveshell import InteractiveShell

class Solution(ipw.VBox):
    
    def __init__(self, shell: InteractiveShell, exercise: str, **kwargs):
        super().__init__(**kwargs)
        self.show_button = ipw.Button(description="Show solution")
        self.exercise = exercise
        self.shell = shell
        self.children = [self.show_button]
        self.show_button.on_click(self.show)
    
    def show(self, widget: ipw.Widget):
        code = self.shell.user_ns.get(self.exercise)
        if isinstance(code, Callable):

            display.display(code.__doc__, display.Code(inspect.getsource(code), language="python"), clear=True, raw=False)
    