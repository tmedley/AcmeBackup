#! /usr/bin/env python3
#
# v0.9
# 091320
# Acme Packet SBC backup script
# Tim Medley
# timmedley@maximus.com
#
# Read a list of SBCs from a list
# Connect to each SBC via SSH and issue the backup-configuration command
# Download the current backup from each SBC via SFTP
#

### import all the modules
import platform
import os
import sys
import logging
from datetime import date
from pathlib import Path
import getpass
from netmiko import ConnectHandler, file_transfer
import paramiko

### setup some logging
# create the logs and sbc-backups folders if they don't already exist
os.makedirs("logs", exist_ok=True)
os.makedirs("sbc-backups", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    filename="logs/acmeBackup.log"
    )
paramiko.util.log_to_file("logs/paramiko.log")

### check what OS we are running on
# we might not need this. I was thinking we might need to adjust the homPath based on OS???
platformType = platform.system()

### set up some variables
# get our date string ready
dateToday = date.today().strftime("%m%d%y").replace('-','')
# set out homePath to save the backups locally
#homePath = str(Path.home() / "Downloads") + "/"
homePath = str(Path.cwd() / "sbc-backups") + "/"
#set the directory on the SBC where the backup files are stored
sbcBackupPath = "/code/bkups/"
sbcBackupDownloaded = 0

welcomeMsg = """
########################################

          MAXIMUS Telecom Team
        Acme Packet SBC Backup Tool

########################################

This tool will load a list of sbc's from
the sbc.txt file then ssh to each sbc
generate a backup and then download that
backup file.
"""

### display a text welcome message and prompt for the SBC ADMIN Password
# we are assuming all the SBCs use the same password, if they don't we're in
# trouble and will have to change that later.
try:
    print(welcomeMsg)
    sbcUsername = "admin"
    sbcPassword = getpass.getpass("Enter the SBC ADMIN account password: ")
except Exception as error:
    print("There was an error accepting your password", error)
else:
    print("\n\nPassword Accepted. All your bases are belong to us.\n\n")

### read a list of SBC IP Addresses to backup from sbc.txt
# stuff each line nicely into a list
# first lets count the number of lines in the file for the progress bar
numberOfSBC = sum(1 for line in open("sbc.txt"))

with open("sbc.txt", "r") as sbcIPAddressFile:
    sbcIPAddressList = sbcIPAddressFile.read().splitlines()



### here we are going to loop through the ipAddresses in our file
# and do all the things
for sbcIPAddress in sbcIPAddressList:

    # populate the netmiko connect profile
    acmeSBC = {
        "device_type" : "linux",
        "ip" : sbcIPAddress,
        "username" : sbcUsername,
        "password" : sbcPassword,
    }

    # Connect to a SBC
    try:
        net_connect = ConnectHandler(**acmeSBC)
        net_connect.enable()

        ### setup our backups file name
        # we are using the SBCs prompt as the basis for our file naming scheme
        # however we need to strip the -, the trailing 01
        # and the # from the enable prompt
        # we then add BU for backup, the date in DDMMYY and the engineers
        # initials, in this case PY for python :)
        # final name should be something like CULACME6300BU122520PY
        sbcDeviceName = net_connect.find_prompt().replace("-","")[:-3]
        sbcBackupFileName = sbcDeviceName + "BU" + dateToday + "PY"

        # tell the sbc to generate a new backup file
        # filename format is: DC SBC_Name ACME BU DATE USER

        acmeBackupCommand = net_connect.send_command("backup-config " + sbcBackupFileName + " running")
    except paramiko.ssh_exception.AuthenticationException as error:
        print("\nAuthentication Error trying to connect to:\033[1;31m " + sbcIPAddress + "\033[0;0m\n\n")
        continue
    except paramiko.ssh_exception.SSHException as error:
        print("\nSSH Error trying to connect to:\033[1;31m " + sbcIPAddress + "\033[0;0m\n\n")
        continue
    except Exception as error:
        print("\nFailed to connect to:\033[1;31m " + sbcIPAddress + "\033[0;0m someone probably fed the Gremlins after midnight, again")
        #sys.exit(1)
        continue

### shouldn't I add this into the above try/except?
# or do else: and the next part?

    try:
        ### setup the file paths
        # we need to add the .gz file extension in our get command, the sbc
        # added it automatically when it did the backup
        sbcBackupFileNameExt = sbcBackupFileName + ".gz"
        sbcBackupFullPath = sbcBackupPath + sbcBackupFileNameExt
        clientBackupFullPath = homePath + sbcBackupFileNameExt
        ### conect the transport
        # we have an established SSH connection from netmiko, could we use
        # that instead of a new transport?
        transportClient = paramiko.Transport(sbcIPAddress)
        transportClient.connect(username = sbcUsername, password = sbcPassword)
        sftpClient = paramiko.SFTPClient.from_transport(transportClient)
        sftpClient.get(sbcBackupFullPath, clientBackupFullPath)

    except:
        print("\nFailed to connect to:\033[1;31m ", sbcIPAddress + "\033[0;0m")
        continue
    else:
        sbcBackupDownloaded += 1


### our loop ends and we can do some cleanup if its not already done
# print some handy dandy info to the log file, probably not needed
logging.info("Variable data:")
logging.info(dateToday)
logging.info(platformType)
logging.info(homePath)
logging.info(sbcIPAddressList)

### disconnect the sessions, it was done in the loop, so this is just in case
# something goes haywire in the loop... probably not needed
net_connect.disconnect()
sftpClient.close()
transportClient.close()

### and we're done. print a note saying so and remind us where the backups were downloaded
print("\n\n\nThe backups have been completed for \033[1;32m" + str(sbcBackupDownloaded) + "\033[0;0m devices.")
print("You will find them here: ", homePath)
print("\nAll sessions have been closed. Have a nice day!\n\n\a")
