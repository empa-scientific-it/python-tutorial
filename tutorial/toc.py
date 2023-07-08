#!/usr/bin/env python
import argparse as ap
import dataclasses
import pathlib
import re

import nbformat
from nbformat import NotebookNode


@dataclasses.dataclass
class TocEntry:
    """A table of contents entry"""

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
    line_re = re.compile(r"(#+)\s+(.+)")
    for line in notebook.splitlines():
        if groups := re.match(line_re, line):
            heading, text, *_ = groups.groups()
            level = len(heading)
            anchor = "-".join(text.replace("`", "").split())
            toc.append(TocEntry(level, text, anchor))
    return toc


def markdown_toc(toc: "list[TocEntry]") -> str:
    """Build a string representation of the toc as a nested markdown list"""
    lines = []
    for entry in toc:
        line = f"{'  ' * entry.level}- [{entry.text}](#{entry.anchor})"
        lines.append(line)
    return "\n".join(lines)


def build_toc(nb_path: pathlib.Path, placeholder: str = "[TOC]") -> NotebookNode:
    """Build a table of contents for a notebook and insert it at the location of a placeholder"""
    # Read the notebook
    nb_obj: NotebookNode = nbformat.read(nb_path, nbformat.NO_CONVERT)
    md_cells = extract_markdown_cells(nb_obj)

    # Build tree
    toc_tree = extract_toc(md_cells)

    # Build toc representation
    toc_repr = markdown_toc(toc_tree)

    # Insert it a the location of a placeholder
    toc_header = "# Table of Contents"

    for cell in nb_obj.cells:
        print(cell)
        if cell.source.startswith(placeholder) or cell.source.startswith(toc_header):
            cell.source = f"{toc_header}\n{toc_repr}"
            cell.cell_type = "markdown"

    return nb_obj


def main():
    """CLI entry point"""
    parser = ap.ArgumentParser()
    parser.add_argument("notebook", type=str, help="Path to the notebook to process")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output path")
    args = parser.parse_args()

    if args.output is None:
        args.output = args.notebook

    output_nb = pathlib.Path(args.output)

    with output_nb.open("w", encoding="utf-8") as file:
        nbformat.write(build_toc(pathlib.Path(args.notebook)), file)


if __name__ == "__main__":
    main()
