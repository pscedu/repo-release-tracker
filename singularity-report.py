import argparse
import sys
import os
from datetime import datetime

import pandas as pd
from github import Github
from tqdm import tqdm
from rich.console import Console
from rich.table import Table

# -----------------------------
# Define repo lists
# -----------------------------
stem_repos = [
    "stride", "nanoplot", "star-fusion", "filtlong", "porechop", "anvio", "funannotate",
    "fastq-tools", "meme-suite", "braker2", "rust", "guppy", "guppy-gpu", "bsmap", "salmon",
    "rnaview", "bioformats2raw", "raw2ometiff", "flash", "blat", "bedops", "genemark-es",
    "augustus", "checkm", "ncview", "bowtie2", "asciigenome", "fastqc", "sra-toolkit", "gatk",
    "hmmer", "bcftools", "raxml", "spades", "busco", "samtools", "bedtools", "bamtools",
    "fastani", "phylip-suite", "blast", "viennarna", "cutadapt", "bismark", "star", "prodigal",
    "bwa", "picard", "hisat2", "abyss", "octave", "tiger", "gent", "methylpy", "fasttree",
    "vcf2maf", "htslib", "kraken2", "aspera-connect", "trimmomatic"
]

utilities_repos = [
    "hashdeep", "dua", "vim", "timewarrior", "libtiff-tools", "wordgrinder", "shellcheck",
    "pandiff", "rich-cli", "jq", "jp", "lowcharts", "btop", "aws-cli", "cwltool", "circos",
    "glances", "fdupes", "graphviz", "browsh", "hyperfine", "dust", "gnuplot", "pandoc", "mc",
    "bat", "flac", "visidata", "octave", "ncdu", "lazygit", "asciinema", "ffmpeg", "imagemagick",
    "rclone"
]

# -----------------------------
# Parse arguments first
# -----------------------------
parser = argparse.ArgumentParser(description="Filter and display GitHub repos by category.")
parser.add_argument("--utilities", action="store_true", help="Show utility repos")
parser.add_argument("--scientific", action="store_true", help="Show scientific (STEM) repos")
parser.add_argument("--repo", type=str, help="Show info for a specific repo only")
args = parser.parse_args()

# Decide which repos to fetch
if args.repo:
    repo_name = args.repo.lower()
    if repo_name in [r.lower() for r in stem_repos] and repo_name in [r.lower() for r in utilities_repos]:
        category = "Both"
    elif repo_name in [r.lower() for r in stem_repos]:
        category = "STEM"
    elif repo_name in [r.lower() for r in utilities_repos]:
        category = "Utility"
    else:
        category = "Unknown"
    repos_to_fetch = [(repo_name, category)]
elif args.utilities and args.scientific:
    repos_to_fetch = [(name, "Utility") for name in utilities_repos] + [(name, "STEM") for name in stem_repos]
elif args.utilities:
    repos_to_fetch = [(name, "Utility") for name in utilities_repos]
elif args.scientific:
    repos_to_fetch = [(name, "STEM") for name in stem_repos]
else:
    repos_to_fetch = [(name, "Utility") for name in utilities_repos] + [(name, "STEM") for name in stem_repos]


# Remove duplicates, keeping "Both" category if necessary
repo_dict = {}
for name, category in repos_to_fetch:
    if name in repo_dict and repo_dict[name] != category:
        repo_dict[name] = "Both"
    else:
        repo_dict[name] = category

repos_to_fetch = list(repo_dict.items())

# -----------------------------
# GitHub authentication
# -----------------------------
secrets_path = os.path.expanduser("~/.GITHUB_SECRETS")
with open(secrets_path) as f:
    token = None
    for line in f:
        if line.startswith("PERSONAL_ACCESS_TOKEN="):
            token = line.strip().split("=", 1)[1]
            break

g = Github(token)

# -----------------------------
# Fetch repo data
# -----------------------------
print("Getting information from GitHub...")
results = []

for repoName, category in tqdm(repos_to_fetch, desc="Fetching repos"):
    try:
        repo = g.get_repo(f"pscedu/singularity-{repoName}")
        latestRelease = repo.get_latest_release()
        release = latestRelease.title or latestRelease.tag_name
        date = str(latestRelease.published_at)[0:10]
        results.append([category, repoName, release, date])
    except Exception:
        results.append([category, repoName, "No release", "N/A"])


# -----------------------------
# Create DataFrame & sort
# -----------------------------
df = pd.DataFrame(results, columns=["Category", "Repo Name", "Latest Version", "Date"])
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.sort_values(by="Date", ascending=False)

# -----------------------------
# Display results in table
# -----------------------------
title = "All Repositories"
if args.utilities and not args.scientific:
    title = "Utility Repositories"
elif args.scientific and not args.utilities:
    title = "Scientific Repositories"

table = Table(title=title, show_lines=True)
table.add_column("Repo Name", style="cyan", no_wrap=True)
table.add_column("Latest Version", style="green")
table.add_column("Date", style="magenta")
table.add_column("Link", style="blue", overflow="fold")
table.add_column("Category", style="yellow")

for _, row in df.iterrows():
    repo_name = row["Repo Name"]
    version = row["Latest Version"]
    date = row["Date"].strftime("%Y-%m-%d") if not pd.isnull(row["Date"]) else "N/A"
    link = f"https://github.com/pscedu/singularity-{repo_name}"
    category = row["Category"]
    table.add_row(repo_name, version, date, link, category)

console = Console()
console.print(table)
