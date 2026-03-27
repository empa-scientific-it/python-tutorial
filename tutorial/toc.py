#!/usr/bin/env python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "typer",
#   "rich",
#   "nbformat"
# ]
# ///
"""CLI script to build a table of contents for a Jupyter notebook."""

import pathlib
import re
from typing import Annotated, NamedTuple

import nbformat
import typer
from nbformat import NotebookNode
from rich.console import Console

__version__ = "0.3.0"

console = Console()
err_console = Console(stderr=True)

APP_HELP = """\
Generate a Markdown table of contents from a Jupyter notebook's headings and
insert it into a designated cell.

[bold]How it works[/bold]

Scans all [italic]markdown cells[/italic] in the notebook for ATX headings
([cyan]#[/cyan], [cyan]##[/cyan], [cyan]###[/cyan] …), skipping headings inside fenced code blocks and
ignoring the TOC header itself to avoid self-referential entries.

For each heading it produces a linked list item whose anchor is derived from
the heading text (lowercased, spaces → hyphens, most punctuation stripped).

[bold]Placeholder cell requirement[/bold]

The TOC is inserted into the first cell whose source starts with either:

  • the placeholder string (default: [cyan]\\[TOC\\][/cyan])
  • an existing [cyan]# Table of Contents[/cyan] heading (allows regeneration)

If no such cell is found the script exits without writing any output.

[bold]Output modes[/bold]

  [green]default[/green]   Writes [cyan]<notebook>.toc.ipynb[/cyan] alongside the original file.
  [green]-o PATH[/green]   Writes to an explicit output path.
  [green]--force[/green]       Overwrites the original notebook in-place.
  [green]--split-cells[/green]   Split multi-heading cells so all TOC links work in Jupyter.

[bold]Examples[/bold]

  [dim]# Generate TOC, write to my_notebook.toc.ipynb[/dim]
  uv run toc.py my_notebook.ipynb

  [dim]# Update the notebook in-place[/dim]
  uv run toc.py my_notebook.ipynb --force

  [dim]# Custom placeholder and output path[/dim]
  uv run toc.py my_notebook.ipynb -p "<!-- toc -->" -o out/notebook.ipynb
"""


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"toc {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="toc",
    help=APP_HELP,
    add_completion=False,
    rich_markup_mode="rich",
)


class TocEntry(NamedTuple):
    """Table of contents entry."""

    level: int
    text: str
    anchor: str


def extract_markdown_cells(notebook: NotebookNode) -> str:
    """Return concatenated content of all markdown cells in the notebook."""
    return "\n".join(
        cell.source for cell in notebook.cells if cell.cell_type == "markdown"
    )


def extract_toc(notebook: str, toc_header: str) -> list[TocEntry]:
    """Parse markdown headings from a string and return TOC entries.

    Ignores headings inside fenced code blocks and skips the TOC header itself.

    Args:
        notebook: String containing markdown content.
        toc_header: Header text for the table of contents (excluded from output).

    Returns:
        List of TocEntry objects (level, text, anchor).
    """
    toc = []
    line_re = re.compile(r"(#+)\s+(.+)")
    is_code_block = False

    for line in notebook.splitlines():
        if line.strip() == toc_header:
            continue

        if line.strip().startswith("```"):
            is_code_block = not is_code_block
            continue

        if is_code_block:
            continue

        if groups := re.match(line_re, line):
            heading, text, *_ = groups.groups()
            level = len(heading)

            anchor = text.replace("`", "").replace(" ", "-")

            toc.append(TocEntry(level, text, anchor))

    return toc


def markdown_toc(toc: list[TocEntry]) -> str:
    """Return a nested markdown list representation of the TOC entries."""
    lines = []
    for entry in toc:
        line = f"{'  ' * entry.level}- [{entry.text}](#{entry.anchor})"
        lines.append(line)
    return "\n".join(lines)


def split_cell(source: str, toc_header: str) -> list[str]:
    """Split a markdown cell source at each heading boundary.

    Respects fenced code blocks (headings inside them are not split points).
    The TOC header line itself is never a split point.

    Returns a list with one entry per segment. Returns ``[source]`` unchanged
    when no split is needed (zero or one heading found).
    """
    line_re = re.compile(r"^(#+)\s+.+")
    is_code_block = False
    segments: list[str] = []
    current_lines: list[str] = []

    for line in source.splitlines(keepends=True):
        stripped = line.strip()

        if stripped.startswith("```"):
            is_code_block = not is_code_block
            current_lines.append(line)
            continue

        if is_code_block or stripped == toc_header:
            current_lines.append(line)
            continue

        if re.match(line_re, line) and current_lines:
            segments.append("".join(current_lines).strip())
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        segments.append("".join(current_lines).strip())

    return segments if len(segments) > 1 else [source]


def split_multi_heading_cells(
    nb_obj: NotebookNode, toc_header: str
) -> tuple[NotebookNode, int]:
    """Replace each markdown cell that contains multiple headings with one cell per heading.

    Returns ``(nb_obj, cells_split_count)``.
    """
    new_cells: list[NotebookNode] = []
    cells_split = 0

    for cell in nb_obj.cells:
        if cell.cell_type != "markdown":
            new_cells.append(cell)
            continue

        segments = split_cell(cell.source, toc_header)
        if len(segments) == 1:
            new_cells.append(cell)
        else:
            cells_split += 1
            for seg in segments:
                new_cells.append(nbformat.v4.new_markdown_cell(seg))

    nb_obj.cells = new_cells
    return nb_obj, cells_split


def build_toc(
    nb_path: pathlib.Path,
    placeholder: str = "[TOC]",
    toc_header: str = "# Table of Contents",
    split_cells: bool = False,
) -> tuple[NotebookNode, bool, bool, int]:
    """Read a notebook, generate a TOC, and insert it at the placeholder cell.

    Args:
        nb_path: Path to the notebook file.
        placeholder: Text to replace with the generated TOC.
        toc_header: Header text for the TOC section.
        split_cells: If True, split multi-heading cells before generating the TOC.

    Returns:
        Tuple of (notebook, toc_replaced, has_headings, cells_split).
    """
    nb_obj: NotebookNode = nbformat.read(nb_path, nbformat.NO_CONVERT)

    cells_split = 0
    if split_cells:
        nb_obj, cells_split = split_multi_heading_cells(nb_obj, toc_header)

    md_cells = extract_markdown_cells(nb_obj)
    toc_tree = extract_toc(md_cells, toc_header)
    has_headings = bool(toc_tree)

    toc_repr = markdown_toc(toc_tree)
    toc_replaced = False

    for cell in nb_obj.cells:
        if cell.source.startswith((placeholder, toc_header)):
            cell.source = f"{toc_header}\n{toc_repr}"
            cell.cell_type = "markdown"
            toc_replaced = True
            break

    return nb_obj, toc_replaced, has_headings, cells_split


@app.command(help=APP_HELP)
def main(
    notebook: Annotated[
        pathlib.Path,
        typer.Argument(
            help="Path to the Jupyter notebook (.ipynb) to process.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    output: Annotated[
        pathlib.Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Output path for the processed notebook. Defaults to [cyan]<notebook>.toc.ipynb[/cyan].",
            rich_help_panel="Output",
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite the [bold]original[/bold] notebook in-place instead of writing a new file.",
            rich_help_panel="Output",
        ),
    ] = False,
    placeholder: Annotated[
        str,
        typer.Option(
            "--placeholder",
            "-p",
            help=r"Placeholder text in a cell to replace with the generated TOC.",
            rich_help_panel="TOC Options",
        ),
    ] = "[TOC]",
    header: Annotated[
        str,
        typer.Option(
            "--header",
            help="Markdown heading to use as the TOC section header.",
            rich_help_panel="TOC Options",
        ),
    ] = "# Table of Contents",
    split_cells: Annotated[
        bool,
        typer.Option(
            "--split-cells",
            "-s",
            help="Split markdown cells that contain multiple headings into one cell per heading. "
            "Recommended — required for TOC links to work correctly in Jupyter.",
            rich_help_panel="TOC Options",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Print debug information during processing.",
            rich_help_panel="Misc",
        ),
    ] = False,
    version: Annotated[  # noqa: ARG001
        bool,
        typer.Option(
            "--version",
            help="Show the version and exit.",
            callback=_version_callback,
            is_eager=True,
            rich_help_panel="Misc",
        ),
    ] = False,
) -> None:
    if force and output is not None:
        err_console.print(
            "[red]Error:[/red] --output and --force are mutually exclusive."
        )
        raise typer.Exit(1)

    if force:
        output_nb = notebook
    elif output is not None:
        if output.suffix != ".ipynb":
            output = output.with_suffix(output.suffix + ".ipynb")
        output_nb = output
    else:
        output_nb = notebook.with_suffix(".toc.ipynb")

    output_nb.parent.mkdir(parents=True, exist_ok=True)

    if verbose:
        console.print(f"[dim]Processing[/dim] [cyan]{notebook}[/cyan] …")

    try:
        toc_notebook, toc_replaced, has_headings, cells_split = build_toc(
            notebook, placeholder, header, split_cells
        )
    except Exception:
        err_console.print_exception()
        raise typer.Exit(1) from None

    if not has_headings:
        err_console.print(
            f"[yellow]Warning:[/yellow] No headings found in [cyan]{notebook}[/cyan]."
        )

    if not toc_replaced:
        err_console.print(
            "[yellow]Warning:[/yellow] No placeholder or TOC cell found — skipping output."
        )
        raise typer.Exit(0)

    with output_nb.open("w", encoding="utf-8") as file:
        nbformat.write(toc_notebook, file)

    if split_cells and cells_split:
        console.print(f"[dim]Split {cells_split} cell(s) with multiple headings.[/dim]")

    if force:
        console.print(f"[green]Updated in-place:[/green] {notebook}")
    else:
        console.print(f"[green]TOC written to:[/green] {output_nb}")


if __name__ == "__main__":
    app()
