# Ok First lets add in our code first and clean it up. Then lets add the stuff for sending emails

#import libraries: PyGithub for accessing github API and pandas for dataframes
from pydoc import html
import sys
#!{sys.executable} -m pip install PyGithub

from github import Github
import pandas as pd
#import libraries for sending emails
import smtplib
from email.message import EmailMessage
from datetime import datetime



#create github instance and gets repo:
g = Github("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")    # says can do 60 requests per hour but there are more than 60.


#get the names of the repos we want to check:

stem_repos = ['stride', 'nanoplot','star-fusion','filtlong','porechop','anvio','funannotate','fastq-tools','meme-suite','braker2','rust','guppy','guppy-gpu','bsmap','salmon','rnaview','bioformats2raw','raw2ometiff','flash','blat','bedops','genemark-es','augustus','checkm','ncview','bowtie2','asciigenome','fastqc','sra-toolkit','gatk','hmmer','bcftools','raxml','spades','busco','samtools','bedtools','bamtools','fastani','phylip-suite','blast','viennarna','cutadapt','bismark','star','prodigal','bwa','picard','hisat2','abyss','octave','tiger','gent','methylpy','fasttree','vcf2maf','htslib','kraken2','aspera-connect','trimmomatic']
utilities_repos = ['hashdeep','dua','vim','timewarrior','libtiff-tools','wordgrinder','shellcheck','pandiff','rich-cli','jq','jp','lowcharts','btop','aws-cli','cwltool','circos','glances','fdupes','graphviz','browsh','hyperfine','dust','gnuplot','pandoc','mc','bat','flac','visidata','octave','ncdu','lazygit','asciinema','ffmpeg','imagemagick','rclone']

#now lets go through them and extract the names, version, and years
#starting with stem and then utilities repo:
print("starting")
stemRepo = []
utilityRepo = []
for repoName in stem_repos:
    try:
        repo = g.get_repo("pscedu/singularity-"+repoName)
        latestRelease = repo.get_latest_release()
        release = latestRelease.title or latestRelease.tag_name
        date = str(latestRelease.published_at)[0:10]
    
        stemRepo.append([repoName, release, date])
        print("finished " + repoName +"\n")
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
print("finished making dataframes")

# ok now let's convert the date column into datetime objects so we can sort by date

df_stem["Date"] = pd.to_datetime(df_stem["Date"], errors="coerce")
df_utility["Date"] = pd.to_datetime(df_utility["Date"], errors="coerce")

df_Sorted_stem = df_stem.sort_values(by = "Date", ascending = False)
df_Sorted_utility = df_utility.sort_values(by = "Date", ascending = False)



#now lets link the release version to their github links as well:
df_Sorted_stem["Latest Version"] = df_Sorted_stem.apply(
    lambda row: f'<a href="https://github.com/pscedu/singularity-{row["STEM Repo Name"]}/releases">{row["Latest Version"]}</a>',
    axis=1
)

df_Sorted_utility["Latest Version"] = df_Sorted_utility.apply(
    lambda row: f'<a href="https://github.com/pscedu/singularity-{row["Utility Repo Name"]}/releases">{row["Latest Version"]}</a>',
    axis=1
)

# now we need to link the repo names to their github links
df_Sorted_stem["STEM Repo Name"] = df_Sorted_stem["STEM Repo Name"].apply(
    lambda x: f'<a href="https://github.com/pscedu/singularity-{x}">{x}</a>'
)

df_Sorted_utility["Utility Repo Name"] = df_Sorted_utility["Utility Repo Name"].apply(
    lambda x: f'<a href="https://github.com/pscedu/singularity-{x}">{x}</a>'
)


# convert the dataframes to html tables:
html_stem = df_Sorted_stem.to_html(index=False, justify='left', escape =False)
html_utility = df_Sorted_utility.to_html(index=False, justify='left', escape =False)


# make email:
message = EmailMessage()
message["Subject"] = f"Singularity Repos Latest Releases - {datetime.now().strftime('%Y-%m-%d')}"
message["From"] = "luism@psc.edu"
message["To"] = "luisjorgerubio@gmail.com", "icaoberg@psc.edu"

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
# send email:a
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login("luism@psc.edu", "ebxh ivrd pxtc zvwc")
    smtp.send_message(message)

print("Email sent successfully!")
# to send it weekly we need to set up a cron job on terminal.
