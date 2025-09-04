import ast
import pathlib


class AstParser:
    """
    Helper class for extraction of function definitions and imports.
    To find all reference solutions:
    Parse the module file using the AST module and retrieve all function definitions and imports.
    For each reference solution store the names of all other functions used inside of it.
    """

    def __init__(self, module_file: pathlib.Path) -> None:
        self.module_file = module_file
        self.function_defs = {}
        self.function_imports = {}
        self.called_function_names = {}

        tree = ast.parse(self.module_file.read_text(encoding="utf-8"))

        for node in tree.body:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                self.function_defs[node.name] = node
            elif isinstance(node, ast.Import | ast.ImportFrom) and hasattr(
                node, "module"
            ):
                for n in node.names:
                    self.function_imports[n.name] = node.module

        for node in tree.body:
            if (
                node in self.function_defs.values()
                and hasattr(node, "name")
                and node.name.startswith("reference_")
            ):
                self.called_function_names[node.name] = self.retrieve_functions(
                    {**self.function_defs, **self.function_imports}, node, {node.name}
                )

    def retrieve_functions(
        self, all_functions: dict, node: object, called_functions: set[object]
    ) -> set[object]:
        """
        Recursively walk the AST tree to retrieve all function definitions in a file
        """

        if isinstance(node, ast.AST):
            for n in ast.walk(node):
                match n:
                    case ast.Call(ast.Name(id=name)):
                        called_functions.add(name)
                        if name in all_functions:
                            called_functions = self.retrieve_functions(
                                all_functions, all_functions[name], called_functions
                            )
                for child in ast.iter_child_nodes(n):
                    called_functions = self.retrieve_functions(
                        all_functions, child, called_functions
                    )

        return called_functions

    def get_solution_code(self, name: str) -> str:
        """
        Find the respective reference solution for the executed function.
        Create a str containing its code and the code of all other functions used,
        whether coming from the same file or an imported one.
        """

        solution_functions = self.called_function_names[f"reference_{name}"]
        solution_code = ""

        for f in solution_functions:
            if f in self.function_defs:
                solution_code += ast.unparse(self.function_defs[f]) + "\n\n"
            elif f in self.function_imports:
                function_file = pathlib.Path(
                    f"{self.function_imports[f].replace('.', '/')}.py"
                )
                if function_file.exists():
                    function_file_tree = ast.parse(
                        function_file.read_text(encoding="utf-8")
                    )
                    for node in function_file_tree.body:
                        if (
                            isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
                            and node.name == f
                        ):
                            solution_code += ast.unparse(node) + "\n\n"

        return solution_code
