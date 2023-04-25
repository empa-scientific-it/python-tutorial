#! /usr/bin/env python
import nbformat
import ipynbname
import pathlib
from IPython.core.getipython import get_ipython
import argparse as ap
import markdown
import markdown.extensions.toc
from nbformat import NotebookNode
import dataclasses
from collections import deque
import re

@dataclasses.dataclass
class TocEntry:
    level: int
    text: str
    anchor: str

def extract_markdown_cells(nb: NotebookNode) -> str:
    """Extract the markdown cells from a notebook"""
    return "\n".join([cell.source for cell in nb.cells if cell.cell_type == "markdown"])




def extract_toc(nb: str) -> "list[TocEntry]":
    tree = deque()
    toc = []    
    line_re = re.compile("(#+)\s+(.+)")
    for line in nb.splitlines():
        if groups := re.match(line_re, line):
            heading, text, *rest = groups.groups()
            level = len(heading)
            anchor = "-".join(text.replace("`", "").split())
            toc.append(TocEntry(level, text, anchor))
    return toc


def represent_toc(toc: "list[TocEntry]") -> str:
    """Build a string representation of the toc as a nested markdown list"""
    lines = []
    for entry in toc:
        line = f"{'  ' * entry.level}- [{entry.text}](#{entry.anchor})"
        lines.append(line)
    return "\n".join(lines)
    

def build_toc(nb_path: pathlib.Path, placeholder: str = "[TOC]") -> NotebookNode:


    # Read the notebook
    nb_obj: NotebookNode = nbformat.read(nb_path, nbformat.NO_CONVERT)
    md_cells = extract_markdown_cells(nb_obj)
    #Build tree
    toc_tree = extract_toc(md_cells)
    #Build toc representation
    toc_repr = represent_toc(toc_tree)
    #Insert it a the location of a placeholder
    #new_cells = [({k: (toc_repr if k == "source" else v) for k,v in cell.items()} if cell.source.startswith(placeholder) else cell) for cell in nb_obj.cells]
    #nb_obj.cells = new_cells
    toc_header = "# Table of Contents"
    for cell in nb_obj.cells:
        print(cell)
        if cell.source.startswith(placeholder) or cell.source.startswith(toc_header):
            cell.source = f"{toc_header}\n{toc_repr}"
            cell.cell_type = "markdown"
   
    return nb_obj
    # Extract the table of contents
    # toc = []
    # for cell in nb_obj.cells:
    #     if cell.cell_type == "markdown" and ce
    # ll.source.startswith("#"):
    #         cell = cell.source.splitlines()[0]

    #         level = len(cell.split()[0])
    #         text = " ".join(cell.split()[1:])
    #         anchor = "-".join(text.replace("`", "").split())


    #         # Add entry to toc
    #         toc.append((level, text, anchor))
    # print(toc)
    # # Format toc
    # toc_str = "# Table of contents\n"
    # level_0 = toc[0][0]  # the first level
    # for level, text, anchor in toc:
    #     toc_str += "{} [{}]({})\n".format("  " * (level - level_0) + "-", text, "#" + anchor)

    # # Add a new cell with the toc content
    # print(toc_str)


def main():
    parser = ap.ArgumentParser()
    parser.add_argument("notebook", type=pathlib.Path, help="Path to the notebook to process")
    args = parser.parse_args()

    new_nb = build_toc(args.notebook)    
    with open(args.notebook, "w") as f:
        nbformat.write(new_nb, f)

if __name__ == "__main__":
    main()