import paramiko
import argparse
import getpass

# ---------- SETTINGS ----------
hostname = "bridges2.psc.edu"
username = "luism"
password = getpass.getpass("Enter your Bridges-2 password: ")

folders_to_check = [
    "/opt/modulefiles/production",
    "/opt/modulefiles/preproduction"
]
# ------------------------------

parser = argparse.ArgumentParser(description="Case-insensitive check if file exists in Bridges-2 folders")
parser.add_argument("filename", help="The name of the file to check (case-insensitive)")
args = parser.parse_args()

filename_lower = args.filename.lower()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password)

found_any = False

for folder in folders_to_check:
    # List files in the folder
    command = f"ls {folder}"
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    if exit_status != 0:
        print(f"⚠️ Could not list directory {folder}")
        continue

    files = stdout.read().decode().split()
    # Compare lowercase
    matches = [f for f in files if f.lower() == filename_lower]

    if matches:
        print(f"✅ Found {args.filename} (case-insensitive match: {matches[0]}) in {folder}")
        found_any = True
    else:
        print(f"❌ {args.filename} not found in {folder}")

if not found_any:
    print(f"❌ {args.filename} not found in production or preproduction.")

ssh.close()


# run in terminal write python FileChecker.py --FileNametoCheck <filename>