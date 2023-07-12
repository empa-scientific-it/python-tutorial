#!/usr/bin/env python
"""CLI script to build a table of contents for an IPython notebook"""
import argparse as ap
import pathlib
import re
from typing import NamedTuple

import nbformat
from nbformat import NotebookNode


class TocEntry(NamedTuple):
    """Table of contents entry"""

    level: int
    text: str
    anchor: str


def extract_markdown_cells(notebook: NotebookNode) -> str:
    """Extract the markdown cells from a notebook"""
    return "\n".join(
        [cell.source for cell in notebook.cells if cell.cell_type == "markdown"]
    )


def extract_toc(notebook: str) -> list[TocEntry]:
    """Extract the table of contents from a markdown string"""
    toc = []

    # Regex trick: use a capture group to match the heading level discarding code blocks
    line_re = re.compile(r"```py.*\n#|^(#{1,6})\s+(.+)", re.MULTILINE)

    for match in re.findall(line_re, notebook):
        if all(match):
            level, text = match
            anchor = "-".join(text.replace("`", "").split())
            toc.append(TocEntry(len(level), text, anchor))

    return toc


def markdown_toc(toc: list[TocEntry]) -> str:
    """Build a string representation of the toc as a nested markdown list"""
    return "\n".join(
        f"{'  ' * entry.level}- [{entry.text}](#{entry.anchor})" for entry in toc
    )


def build_toc(nb_path: pathlib.Path, placeholder: str = "[TOC]") -> NotebookNode:
    """Build a table of contents for a notebook and insert it at the location of a placeholder"""
    # Read the notebook
    nb_obj: NotebookNode = nbformat.read(nb_path, nbformat.NO_CONVERT)

    # Extract markdown cells
    md_cells = extract_markdown_cells(nb_obj)

    # Build tree
    toc_tree = extract_toc(md_cells)

    # Build toc representation
    toc_repr = markdown_toc(toc_tree)

    # Insert it a the location of a placeholder
    toc_header = "# Table of Contents"

    for cell in nb_obj.cells:
        if cell.source.startswith((placeholder, toc_header)):
            cell.source = f"{toc_header}\n{toc_repr}"
            cell.cell_type = "markdown"

    return nb_obj


def main():
    """CLI entry point"""
    parser = ap.ArgumentParser(
        description="Build a table of contents for an IPython notebook"
    )
    parser.add_argument("notebook", type=str, help="Path to the notebook to process")
    parser.add_argument(
        "--output", "-o", type=str, default=None, help="Path to the output notebook"
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        default=False,
        help="Force overwrite of original notebook",
    )
    args = parser.parse_args()

    if not (input_nb := pathlib.Path(args.notebook)).exists():
        raise FileNotFoundError(f"Notebook '{input_nb}' does not exist.")

    if args.output is None:
        output_nb = input_nb.with_suffix(".toc.ipynb")
    else:
        output_nb = pathlib.Path(args.output)

    with output_nb.open("w", encoding="utf-8") as file:
        nbformat.write(build_toc(input_nb), file)

    if args.force:
        input_nb.unlink()
        output_nb.rename(input_nb)


if __name__ == "__main__":
    main()
