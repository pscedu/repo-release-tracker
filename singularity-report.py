# code from yesterday that gets the latest releases of the singularity repos :

# Ok First lets add in our code first and clean it up. Then lets add the stuff for sending emails

# import libraries: PyGithub for accessing github API and pandas for dataframes
from pydoc import html
import sys

print(sys.executable)

from github import Github
import pandas as pd

# libaries for creating spreadsheets
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side

from datetime import datetime

# ok so need to just convert to just make csv file and then make prompt using argument parser for input arguments
# then we need to just show the part of csv file that has the specific repos

# create github instance and gets repo:
secrets_path = os.path.expanduser("~/.GITHUB_SECRETS")

token = None
with open(secrets_path) as f:
    for line in f:
        if line.startswith("PERSONAL_ACCESS_TOKEN="):
            token = line.strip().split("=", 1)[1]
            break

g = Github(token)  # says can do 60 requests per hour but there are more than 60.

# get the names of the repos we want to check:

stem_repos = [
    "stride",
    "nanoplot",
    "star-fusion",
    "filtlong",
    "porechop",
    "anvio",
    "funannotate",
    "fastq-tools",
    "meme-suite",
    "braker2",
    "rust",
    "guppy",
    "guppy-gpu",
    "bsmap",
    "salmon",
    "rnaview",
    "bioformats2raw",
    "raw2ometiff",
    "flash",
    "blat",
    "bedops",
    "genemark-es",
    "augustus",
    "checkm",
    "ncview",
    "bowtie2",
    "asciigenome",
    "fastqc",
    "sra-toolkit",
    "gatk",
    "hmmer",
    "bcftools",
    "raxml",
    "spades",
    "busco",
    "samtools",
    "bedtools",
    "bamtools",
    "fastani",
    "phylip-suite",
    "blast",
    "viennarna",
    "cutadapt",
    "bismark",
    "star",
    "prodigal",
    "bwa",
    "picard",
    "hisat2",
    "abyss",
    "octave",
    "tiger",
    "gent",
    "methylpy",
    "fasttree",
    "vcf2maf",
    "htslib",
    "kraken2",
    "aspera-connect",
    "trimmomatic",
]
utilities_repos = [
    "hashdeep",
    "dua",
    "vim",
    "timewarrior",
    "libtiff-tools",
    "wordgrinder",
    "shellcheck",
    "pandiff",
    "rich-cli",
    "jq",
    "jp",
    "lowcharts",
    "btop",
    "aws-cli",
    "cwltool",
    "circos",
    "glances",
    "fdupes",
    "graphviz",
    "browsh",
    "hyperfine",
    "dust",
    "gnuplot",
    "pandoc",
    "mc",
    "bat",
    "flac",
    "visidata",
    "octave",
    "ncdu",
    "lazygit",
    "asciinema",
    "ffmpeg",
    "imagemagick",
    "rclone",
]

# now lets go through them and extract the names, version, and years
# starting with stem and then utilities repo:
print("starting")
stemRepo = []
utilityRepo = []
for repoName in stem_repos:
    try:
        repo = g.get_repo("pscedu/singularity-" + repoName)
        latestRelease = repo.get_latest_release()
        release = latestRelease.title or latestRelease.tag_name
        date = str(latestRelease.published_at)[0:10]

        stemRepo.append([repoName, release, date])
        print("finished " + repoName + "\n")
    except Exception as e:
        stemRepo.append([repoName, "No release", "N/A"])
# now for utility repos:
for repoName in utilities_repos:
    try:
        repo = g.get_repo("pscedu/singularity-" + repoName)
        latestRelease = repo.get_latest_release()
        release = latestRelease.title or latestRelease.tag_name
        date = str(latestRelease.published_at)[0:10]

        utilityRepo.append([repoName, release, date])
    except Exception as e:
        utilityRepo.append([repoName, "No release", "N/A"])

# Now we need to figure out how to sort them by category.


# now lets make the dataframes for the repos:
df_stem = pd.DataFrame(stemRepo, columns=["Repo Name", "Latest Version", "Date"])
df_utility = pd.DataFrame(utilityRepo, columns=["Repo Name", "Latest Version", "Date"])
print("finished making dataframes")

# now lets combine the dataframes into one dataframe and create new category column:

df_stem["Category"] = "STEM"  # adds category column
df_utility["Category"] = "Utility"

combined_df = pd.concat(
    [df_stem, df_utility], ignore_index=True
)  # combines without losing duplicates

category_map = combined_df.groupby("Repo Name")["Category"].apply(
    lambda x: "Both" if len(set(x)) > 1 else x.iloc[0]
)
combined_df["Category"] = combined_df["Repo Name"].map(
    category_map
)  # removes duplicates and adds updated category

combined_df = combined_df.drop_duplicates(
    subset=["Repo Name"]
)  # removes duplicates based on repo name


# ok now let's sort these by date(descending order). and then rearrange the columns

combined_df["Date"] = pd.to_datetime(combined_df["Date"], errors="coerce")
sorted_combined_df = combined_df.sort_values(by="Date", ascending=False)


# now lets rearrange the columns to have  category first, then repo name, then latest version, and then date
sorted_combined_df = sorted_combined_df[
    ["Category", "Repo Name", "Latest Version", "Date"]
]
print(sorted_combined_df)

# code for displaying separate categories:

import argparse
from rich.console import Console
from rich.table import Table

import argparse

parser = argparse.ArgumentParser(
    description="Filter and display GitHub repos by category."
)

parser.add_argument("--utilities", action="store_true", help="Show utility repos")

parser.add_argument(
    "--scientific", action="store_true", help="Show scientific (stem) repos"
)

args = parser.parse_args()

if args.utilities and args.scientific:
    title = "All Repositories"
    filtered_df = sorted_combined_df
elif args.utilities:
    title = "Utility Repositories"
    filtered_df = sorted_combined_df[
        sorted_combined_df["Category"].isin(["Utility", "Both"])
    ]
elif args.scientific:
    title = "Scientific Repositories"
    filtered_df = sorted_combined_df[
        sorted_combined_df["Category"].isin(["STEM", "Both"])
    ]
else:
    title = "All Repositories"
    filtered_df = sorted_combined_df

table = Table(title=title, show_lines=True)

table.add_column("Repo Name", style="cyan", no_wrap=True)
table.add_column("Latest Version", style="green")
table.add_column("Date", style="magenta")
table.add_column("Link", style="blue", overflow="fold")

for _, row in filtered_df.iterrows():
    repo_name = row["Repo Name"]
    version = row["Latest Version"]
    date = row["Date"].strftime("%Y-%m-%d") if not pd.isnull(row["Date"]) else "N/A"
    link = f"https://github.com/pscedu/singularity-{repo_name}"
    table.add_row(repo_name, version, date, link)

console = Console()
console.print(table)
