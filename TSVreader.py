#!/usr/bin/env python3

import argparse
import sys
import re
import pandas as pd
import requests
from io import StringIO
from rich.console import Console
from rich.table import Table
import pydoc  # for pager

# Raw GitHub URL for data.tsv produced by your generator script
TSV_URL = "https://raw.githubusercontent.com/pscedu/singularity/main/data.tsv"

def download_tsv(url: str) -> pd.DataFrame:
    """Download a TSV file from GitHub and return as DataFrame."""
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return pd.read_csv(StringIO(r.text), sep="\t")

def style_cell(value) -> str:
    """
    Render booleans with emoji: True -> green check, False -> red cross.
    If value looks like a timestamp, trim to YYYY-MM-DD.
    """
    s = str(value).strip()

    # Booleans -> emoji
    if s == "True":
        return "[green]✅[/green]"
    if s == "False":
        return "[red]❌[/red]"

    # ISO timestamp -> YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}T", s):
        return s.split("T")[0]

    return s  # leave 'None' and everything else unchanged

def display_table(df: pd.DataFrame) -> None:
    """
    Display DataFrame as a Rich table and show it in a pager (like 'less').
    Note: pager view is plain text (no ANSI colors), but emoji render fine.
    """
    console = Console(record=True)
    table = Table(show_header=True, header_style="bold magenta", show_lines=True)

    # Add columns
    for col in df.columns:
        table.add_column(str(col))

    # Add rows
    for _, row in df.iterrows():
        styled = [style_cell(cell) for cell in row]
        table.add_row(*styled)

    # Render to console buffer, then page the exported text
    console.print(table)
    text = console.export_text()  # plain text for pager
    pydoc.pager(text)

def main():
    parser = argparse.ArgumentParser(
        description="Display data.tsv from GitHub with optional filters (paged like 'less')."
    )
    parser.add_argument("--utilities", action="store_true", help="Show only Utility category")
    parser.add_argument("--scientific", action="store_true", help="Show only Scientific Tool category")
    parser.add_argument("--vis", action="store_true", help="Show only Remote Desktop App category")
    parser.add_argument("--tool", metavar="<tool_name>", type=str, help="Show only the tool whose Name matches exactly")
    parser.add_argument("--all", action="store_true", help="Show all categories (overrides category filters)")

    # If no args at all, show help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)

    args = parser.parse_args()

    # Validate --tool nonempty if provided
    if args.tool is not None and not args.tool.strip():
        raise SystemExit("Error: --tool requires a non-empty <tool_name>.")

    # Load TSV
    df = download_tsv(TSV_URL)

    # Ensure required columns
    if "Category" not in df.columns:
        raise SystemExit("Error: 'Category' column not found in TSV.")
    if "Name" not in df.columns:
        raise SystemExit("Error: 'Name' column not found in TSV.")

    # Normalize/clean
    df["Category"] = df["Category"].astype(str).str.strip()
    df["Name"] = df["Name"].astype(str).str.strip()

    # Replace specific category names
    df["Category"] = df["Category"].replace({
        "Remote Desktop Application": "Remote Desktop App",
        "Scientific tool": "Scientific Tool"
    })

    # If --tool is provided, it takes precedence over other filters
    if args.tool:
        tool_query = args.tool.strip()
        df_tool = df[df["Name"] == tool_query].reset_index(drop=True)
        if df_tool.empty:
            # Show a small hint with close names (case-insensitive contains)
            similar = df[df["Name"].str.contains(re.escape(tool_query), case=False, na=False)]["Name"].unique().tolist()
            if similar:
                hint = " Did you mean: " + ", ".join(similar[:10]) + ("..." if len(similar) > 10 else "")
            else:
                hint = ""
            raise SystemExit(f"Error: Tool '{tool_query}' not found in the 'Name' column.{hint}")
        display_table(df_tool)
        return

    # Category filtering (skipped if --all)
    cat_norm = df["Category"].str.lower().str.strip()
    if not args.all:
        wanted = []
        if args.utilities:
            wanted.append("utility")
        if args.scientific:
            wanted.append("scientific tool")  # normalized for comparison
        if args.vis:
            wanted.append("remote desktop app")

        if wanted:
            mask = pd.Series(False, index=df.index)
            for w in wanted:
                mask |= (cat_norm == w)
            df = df[mask].reset_index(drop=True)

    display_table(df)

if __name__ == "__main__":
    main()