import ipywidgets as ipw
from IPython import  display
from typing import Dict, Any, Callable
import inspect
from IPython.core.interactiveshell import InteractiveShell

class Solution(ipw.VBox):
    
    def __init__(self, ns: Callable, exercise: str, **kwargs):
        super().__init__(**kwargs)
        self.show_button = ipw.Button(description=f"Solution exercise: {exercise}")
        self.cell = ipw.Textarea()
        self.ns = ns
        self.children = [self.show_button, self.cell]
        self.show_button.on_click(self.show)
    
    def show(self, widget: ipw.Widget):
        display.display(self.ns.__doc__, display.Code(inspect.getsource(self.ns), language="python"), clear=True, raw=False)
        self.cell.value.set(display.Code(inspect.getsource(self.ns)))