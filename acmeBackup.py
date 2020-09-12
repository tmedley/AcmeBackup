#
# v0.7 091220
# Acme Packet SBC backup script
# Tim Medley
# timmedley@maximus.com
#
# Read a list of SBCs from a list
# Connect to each SBC via SSH and issue the backup-configuration command
# Download the current backup from each SBC via SFTP
#

# import all the modules
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
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    filename="acmeBackup.log"
    )

### check what OS we are running on
# we might not need this. I was thinking we might need to adjust the homPath based on OS???
platformType = platform.system()

### set up some variables
dateToday = date.today().strftime("%m%d%Y").replace('-','')
homePath = str(Path.home() / "Downloads") + "/"
sbcBackupPath = "/code/bkups/"

welcomeMsg = """
########################################

          MAXIMUS Telecom Team
        Acme Packet SBC Backup Tool

########################################

This tool will load a list of sbc's from
the sbc.csv file then ssh to each sbc
generate a backup and then download that
backup file.
"""


### read a list of SBC IP Addresses to backup from sbc.txt
sbcIPAddressFile = open("sbc.txt")
sbcIPAddressList = sbcIPAddressFile.read().splitlines()


### display a text welcome message and prompt for the SBC ADMIN Password
# we are assuming all the SBCs use the same password.
try:
    print(welcomeMsg)
    sbcUsername = "admin"
    sbcPassword = getpass.getpass("Enter the SBC ADMIN account password: ")
except Exception as error:
    print("There was an error accepting your password", error)
else:
    print("Thank you")



### here we are going to loop through the ipAddresses in our file
# and do all the things
for ipAddress in sbcIPAddressList:

    # populate the netmiko connect profile
    acmeSBC = {
        "device_type" : "linux",
        "ip" : ipAddress,
        "username" : sbcUsername,
        "password" : sbcPassword,
    }

    # Connect to a device
    try:
        net_connect = ConnectHandler(**acmeSBC)
        net_connect.enable()

        #print(net_connect.find_prompt())

        # setup our backups file name

        # we are using the SBCs prompt as the basis for our file naming scheme
        # however we need to strip the -, the trailing 01
        # and the # from the enable prompt
        # we then add BU for backup, the date in DDMMYYYY and the engineers
        # initials, in this case PY for python :)
        # final name should be something like CULACME6300BU12252020PY
        sbcDeviceName = net_connect.find_prompt().replace("-","")[:-3]
        backupFileName = sbcDeviceName + "BU" + dateToday + "PY"

        print("\nSSH Connection to: " + ipAddress + " " + sbcDeviceName)
        print(sbcBackupPath + backupFileName)

        # tell the sbc to generate a new backup file
        # filename format is: DC SBC_Name ACME BU DATE USER

        acmeBackupCommand = net_connect.send_command("backup-config " + backupFileName + " running")
        #sbcCommandOutput = net_connect.send_command("display-backups")
    except:
        print("\nFailed to connect to: " + str(ipAddress))
        net_connect.disconnect()
        sys.exit(1)


### shouldn't I add this into the above try/except?
# or do else: and the next part?

    try:
        # setup the file paths
        # we need to add the .gz file extension in our get command, the sbc
        # added it automatically when it did the backup
        backupFileNameExt = backupFileName + ".gz"
        sbcBackupFullPath = sbcBackupPath + backupFileNameExt
        clientBackupFullPath = homePath + backupFileNameExt

        print("\nSFTP Connection to: " + ipAddress)
        print("SBC Path: " + sbcBackupFullPath + " Local Client Path: " + clientBackupFullPath)

        # conect and thy
        transportClient = paramiko.Transport(ipAddress)
        transportClient.connect(username = sbcUsername, password = sbcPassword)
        sftpClient = paramiko.SFTPClient.from_transport(transportClient)
        sftpClient.get(sbcBackupFullPath, clientBackupFullPath)
    except:
        print("\nFailed to connect to: " + str(ipAddress))
        net_connect.disconnect()
        sftpClient.close()
        transportClient.close()
        sys.exit(1)


### our loop ends and we can do some cleanup if its not already done
# print some handy dandy info to the log file, probably not needed
logging.info("Variable data:")
logging.info(dateToday)
logging.info(platformType)
logging.info(homePath)
logging.info(backupFileNameExt)
logging.info(sbcIPAddressList)

### disconnect the sessions, it was done in the loop, so this is just in case
# something goes haywire in the loop... probably not needed
net_connect.disconnect()
sftpClient.close()
transportClient.close()

### and we're done. print a note saying so and remind us where the backups were downloaded
print("\nThe backups have been completed. Find them in your downloads directory: " + str(homePath))
print("\nAll sessions have been closed. Have a nice day!\n\n\a")
