# Ok First lets add in our code first and clean it up. Then lets add the stuff for sending emails

#import libraries: PyGithub for accessing github API and pandas for dataframes
import sys
!{sys.executable} -m pip install PyGithub

from github import Github
import pandas as pd
#import libraries for sending emails
import smtplib
from email.message import EmailMessage

#create github instance and gets repo:
g = Github("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")    # says can do 60 requests per hour but there are more than 60.


#get the names of the repos we want to check:

stem_repos = ['stride', 'nanoplot','star-fusion','filtlong','porechop','anvio','funannotate','fastq-tools','meme-suite','braker2','rust','guppy','guppy-gpu','bsmap','salmon','rnaview','bioformats2raw','raw2ometiff','flash','blat','bedops','genemark-es','augustus','checkm','ncview','bowtie2','asciigenome','fastqc','sra-toolkit','gatk','hmmer','bcftools','raxml','spades','busco','samtools','bedtools','bamtools','fastani','phylip-suite','blast','viennarna','cutadapt','bismark','star','prodigal','bwa','picard','hisat2','abyss','octave','tiger','gent','methylpy','fasttree','vcf2maf','htslib','kraken2','aspera-connect','trimmomatic']
utilities_repos = ['hashdeep','dua','vim','timewarrior','libtiff-tools','wordgrinder','shellcheck','pandiff','rich-cli','jq','jp','lowcharts','btop','aws-cli','cwltool','circos','glances','fdupes','graphviz','browsh','hyperfine','dust','gnuplot','pandoc','mc','bat','flac','visidata','octave','ncdu','lazygit','asciinema','ffmpeg','imagemagick','rclone']

#now lets go through them and extract the names, version, and years
#starting with stem and then utilities repo:
stemRepo = []
utilityRepo = []
for repoName in stem_repos:
    try:
        repo = g.get_repo("pscedu/singularity-"+repoName)
        latestRelease = repo.get_latest_release()
        release = latestRelease.title or latestRelease.tag_name
        date = str(latestRelease.published_at)[0:10]
    
        stemRepo.append([repoName, release, date])
    except Exception as e:
        stemRepo.append([repoName, "No release", "N/A"])
#now for utility repos:
for repoName in utilities_repos:
    try:
        repo = g.get_repo("pscedu/singularity-"+repoName)
        latestRelease = repo.get_latest_release()
        release = latestRelease.title or latestRelease.tag_name
        date = str(latestRelease.published_at)[0:10]
    
        utilityRepo.append([repoName, release, date])
    except Exception as e:
        utilityRepo.append([repoName, "No release", "N/A"])


#now lets make the dataframes for the repos:
df_stem = pd.DataFrame(stemRepo, columns = ["STEM Repo Name", "Latest Version", "Date"])
df_utility = pd.DataFrame(utilityRepo, columns = ["Utility Repo Name", "Latest Version", "Date"])

# ok now let's convert the date column into datetime objects so we can sort by date

df_stem["Date"] = pd.to_datetime(df_stem["Date"], errors="coerce")
df_utility["Date"] = pd.to_datetime(df_utility["Date"], errors="coerce")

df_Sorted_stem = df_stem.sort_values(by = "Date", ascending = False)
df_Sorted_utility = df_utility.sort_values(by = "Date", ascending = False)

# convert the dataframes to html tables:
html_stem = df_Sorted_stem.to_html(index=False, justify='left')
html_utility = df_Sorted_utility.to_html(index=False, justify='left')

# make email:
message = EmailMessage()
message["Subject"] = "Singularity Repos Latest Releases"
message["From"] = "luism@psc.edu"
message["To"] = "icaoberg@psc.edu"

message.add_alternative(f"""
<html>
<body>
<h1>Latest Releases of Singularity Repos</h1>
<h2>STEM Repos:</h2>
{html_stem}
<h2>Utility Repos:</h2>
{html_utility}
</body>
</html>
""", subtype="html")
# send email:
with smtplib.SMTP_SSL("smtp.gmail.com") as smtp:
    smtp.login("luism@psc.edu", "HelloB@@mer2169")
    smtp.send_message(message)

# to send it weekly we need to set up a cron job on terminal.
