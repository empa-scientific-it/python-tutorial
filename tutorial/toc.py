#!/usr/bin/env python
# ruff: noqa G004
"""CLI script to build a table of contents for an IPython notebook"""

import argparse as ap
import logging
import pathlib
import re
import sys
from collections import namedtuple

import nbformat
from nbformat import NotebookNode

__version__ = "0.1.1"

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("toc")

TocEntry = namedtuple("TocEntry", ["level", "text", "anchor"])


def extract_markdown_cells(notebook: NotebookNode) -> str:
    """Extract the markdown cells from a notebook

    Args:
        notebook: A notebook object

    Returns:
        str: Concatenated content of all markdown cells
    """
    return "\n".join(
        [cell.source for cell in notebook.cells if cell.cell_type == "markdown"]
    )


def extract_toc(notebook: str) -> list[TocEntry]:
    """Extract the table of contents from a markdown string

    Parses markdown headings (lines starting with #) and converts them to TOC entries.
    Each entry includes the heading level, text, and an anchor derived from the text.

    Args:
        notebook: String containing markdown content

    Returns:
        list[TocEntry]: List of table of contents entries
    """
    toc = []
    line_re = re.compile(r"(#+)\s+(.+)")
    line_num = 0

    for line in notebook.splitlines():
        line_num += 1
        if groups := re.match(line_re, line):
            try:
                heading, text, *_ = groups.groups()
                level = len(heading)

                # Clean the text to make a proper anchor
                clean_text = text.replace("`", "")
                # Remove any other special characters that might break anchors
                clean_text = re.sub(r"[^\w\s-]", "", clean_text)
                anchor = "-".join(clean_text.lower().split())

                toc.append(TocEntry(level, text, anchor))
                logger.debug(f"Found heading (level {level}): {text}")
            except Exception as e:
                logger.warning(f"Error processing heading at line {line_num}: {e}")

    return toc


def markdown_toc(toc: list[TocEntry]) -> str:
    """Build a string representation of the toc as a nested markdown list

    Args:
        toc: List of TocEntry objects

    Returns:
        str: Markdown-formatted table of contents with proper indentation
    """
    lines = []
    for entry in toc:
        line = f"{'  ' * entry.level}- [{entry.text}](#{entry.anchor})"
        lines.append(line)
    return "\n".join(lines)


def build_toc(
    nb_path: pathlib.Path,
    placeholder: str = "[TOC]",
    toc_header: str = "# Table of Contents",
) -> tuple[NotebookNode, bool]:
    """Build a table of contents for a notebook and insert it at the location of a placeholder

    Args:
        nb_path: Path to the notebook file
        placeholder: The text to replace with the generated TOC (default: "[TOC]")
        toc_header: The header text to use for the TOC (default: "# Table of Contents")

    Returns:
        tuple[NotebookNode, bool]: The notebook with TOC inserted and a boolean indicating if placeholder was found
    """
    # Read the notebook
    try:
        nb_obj: NotebookNode = nbformat.read(nb_path, nbformat.NO_CONVERT)
    except Exception as e:
        logger.error(f"Failed to read notebook '{nb_path}': {e}")
        raise

    md_cells = extract_markdown_cells(nb_obj)

    # Build tree
    toc_tree = extract_toc(md_cells)

    if not toc_tree:
        logger.warning(f"No headings found in notebook '{nb_path}'")

    # Build toc representation
    toc_repr = markdown_toc(toc_tree)

    # Insert it at the location of a placeholder
    toc_replaced = False

    for cell in nb_obj.cells:
        if cell.source.startswith((placeholder, toc_header)):
            cell.source = f"{toc_header}\n{toc_repr}"
            cell.cell_type = "markdown"
            toc_replaced = True
            break

    if not toc_replaced:
        logger.warning(
            f"Placeholder '{placeholder}' or heading '{toc_header}' not found in notebook"
        )

    return nb_obj, toc_replaced


def main():
    """CLI entry point"""
    parser = ap.ArgumentParser(
        description="Build a table of contents for an IPython notebook",
        epilog="""
        This script extracts headings from markdown cells in a Jupyter notebook and
        generates a markdown-formatted table of contents. The TOC is inserted into
        the notebook at the location of a placeholder (default: '[TOC]') or where
        a '# Table of Contents' heading exists. Links in the TOC point to notebook
        anchors created from the heading text.
        """,
        formatter_class=ap.RawDescriptionHelpFormatter,
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
    parser.add_argument(
        "--placeholder",
        "-p",
        type=str,
        default="[TOC]",
        help="Placeholder text to replace with the TOC (default: '[TOC]')",
    )
    parser.add_argument(
        "--header",
        type=str,
        default="# Table of Contents",
        help="Header text for the TOC (default: '# Table of Contents')",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    args = parser.parse_args()

    # Set logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validate input file
    try:
        input_nb = pathlib.Path(args.notebook)
        if not input_nb.exists():
            logger.error(f"Input file not found: {input_nb}")
            sys.exit(1)
        if not input_nb.is_file():
            logger.error(f"Input path is not a file: {input_nb}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error processing input path: {e}")
        sys.exit(1)

    # Set output file path
    if args.output is None:
        output_nb = input_nb.with_suffix(".toc.ipynb")
    else:
        output_nb = pathlib.Path(args.output)

    # Create output directory if it doesn't exist
    output_nb.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Generate TOC and write to output file
        logger.info(f"Processing notebook: {input_nb}")
        toc_notebook, toc_replaced = build_toc(input_nb, args.placeholder, args.header)

        if not toc_replaced:
            logger.warning("Skipping output - no placeholder found in notebook")
            sys.exit(0)  # Exit with success code since it's not an error

        with output_nb.open("w", encoding="utf-8") as file:
            nbformat.write(toc_notebook, file)
        logger.info(f"TOC written to: {output_nb}")

        # Handle force option
        if args.force:
            logger.info(f"Replacing original notebook with TOC version")
            input_nb.unlink()
            output_nb.rename(input_nb)
            logger.info(f"Original notebook replaced with: {input_nb}")
    except Exception as e:
        logger.error(f"Error processing notebook: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
