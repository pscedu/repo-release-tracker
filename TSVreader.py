#!/usr/bin/env python3

import argparse
import pandas as pd
import requests
from io import StringIO
from rich.console import Console
from rich.table import Table

# Fixed GitHub TSV link
TSV_URL = "https://raw.githubusercontent.com/pscedu/singularity/refs/heads/main/data.tsv"

def download_tsv(url):
    """Download a TSV file from the given GitHub URL."""
    response = requests.get(url)
    response.raise_for_status()
    return pd.read_csv(StringIO(response.text), sep='\t')

def display_table(df):
    """Display DataFrame as a table using Rich."""
    console = Console()
    table = Table(show_header=True, header_style="bold magenta", show_lines=True)

    # Add columns
    for col in df.columns:
        table.add_column(str(col))

    # Add rows
    for _, row in df.iterrows():
        table.add_row(*[str(cell) for cell in row])

    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="Display data.tsv from GitHub with optional filters.")
    parser.add_argument("--utilities", action="store_true", help="Show only utility data")
    parser.add_argument("--scientific", action="store_true", help="Show only scientific tool data")
    parser.add_argument("--vis", action="store_true", help="Show only remote desktop application data")
    args = parser.parse_args()

    # Download TSV
    df = download_tsv(TSV_URL)

    # Normalize Category column
    if "Category" in df.columns:
        df['Category'] = df['Category'].astype(str).str.strip().str.lower()

    # Build filter list
    filters = []
    if args.utilities:
        filters.append("utility")
    if args.scientific:
        filters.append("scientific tool")
    if args.vis:
        filters.append("remote desktop application")

    # Apply filters if any specified
    if filters:
        # Create a boolean mask for rows matching any of the filters
        mask = False
        for f in filters:
            mask |= df['Category'].str.contains(f, na=False)
        df = df[mask]

    # Display table
    display_table(df)

if __name__ == "__main__":
    main()
# Run this script with: python TSVreader.py --utilities --scientific or --vis for remote desktop app.