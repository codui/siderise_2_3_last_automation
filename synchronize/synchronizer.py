import os
import time

import paramiko
from dotenv import load_dotenv

load_dotenv()
hostname = os.getenv("HOSTNAME")
username = os.getenv("USERNAME")
print(f"{hostname}")
print(f"{username}")

key_path = os.path.expanduser("synchronize/id_ed25519")


remote_path = "/whatapp_bot/chats"
local_path = "chats"


# Create client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connecting to the host
ssh.connect(hostname, username=username, key_filename=key_path)

# SFTP for downloading
sftp = ssh.open_sftp()

# Local folder is exists
os.makedirs(local_path, exist_ok=True)

while True:
    # Get local folders
    local_folders = os.listdir(local_path)

    # Get remote folders
    remote_folders = sftp.listdir(remote_path)

    # Synchronize folders
    for remote_folder in remote_folders:
        if remote_folder not in local_folders:
            os.mkdir(f"{local_path}/{remote_folder}")
            print(f"[Folder] new folder was created: {remote_folder}")

    # Get local folders
    local_folders = os.listdir(local_path)

    # Synchronize files in folders
    for local_folder in local_folders:
        local_files = os.listdir(f"{local_path}/{local_folder}")
        remote_files = sftp.listdir(f"{remote_path}/{local_folder}")

        for remote_file in remote_files:
            if remote_file not in local_files:
                sftp.get(
                    f"{remote_path}/{local_folder}/{remote_file}",
                    f"{local_path}/{local_folder}/{remote_file}",
                )
                print(f"[File] new file was downloaded: {remote_file}")

    print("[Synchonize] Wait for new files/folders...")
    time.sleep(1)
