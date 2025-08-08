import os

folders_to_check = [
    "/opt/modulefiles/production",
    "/opt/modulefiles/preproduction"
]

filename_to_check = input("Enter the filename to check: ").lower()

found_any = False

for folder in folders_to_check:
    try:
        files = os.listdir(folder)
        matches = [f for f in files if f.lower() == filename_to_check]
        
        if matches:
            print(f"✅ Found {matches[0]} in {folder}")
            found_any = True
        else:
            print(f"❌ {filename_to_check} not found in {folder}")
    except FileNotFoundError:
        print(f"⚠️ Folder {folder} does not exist or cannot be accessed")

if not found_any:
    print(f"❌ {filename_to_check} not found in production or preproduction.")
