import nbformat
import ipynbname
import pathlib
from IPython.core.getipython import get_ipython


def build_toc() -> None:
    # Get notebook path
    print(globals())
    nb_path = None
    try:
        nb_name = ipynbname.name() + ".ipynb"
    except FileNotFoundError:
        try:
            nb_name = globals()['__vsc_ipynb_file__']
        except KeyError:
            raise RuntimeError("Notebook name is undefined")
        else:
            nb_path = pathlib.Path(nb_name)

    nb_path = nb_path or pathlib.Path(__file__).parents[1] / nb_name

    # Read the notebook
    nb_obj = nbformat.read(nb_path, nbformat.NO_CONVERT)

    # Extract the table of contents
    toc = []
    for cell in nb_obj.cells:
        if cell.cell_type == "markdown" and cell.source.startswith("#"):
            cell = cell.source.splitlines()[0]

            level = len(cell.split()[0])
            text = " ".join(cell.split()[1:])
            anchor = "-".join(text.replace("`", "").split())

            # Add entry to toc
            toc.append((level, text, anchor))

    # Format toc
    toc_str = "# Table of contents\n"
    level_0 = toc[0][0]  # the first level
    for level, text, anchor in toc:
        toc_str += "{} [{}]({})\n".format("  " * (level - level_0) + "-", text, "#" + anchor)

    # Add a new cell with the toc content
    get_ipython().set_next_input(toc_str)
