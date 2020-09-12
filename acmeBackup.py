#
# v0.1 091020
# Acme SBC backup script
# Tim Medley
# timmedley@maximus.com
#
# Read a list of SBCs from a list
# Connect to each SBC and issue the backup-configuration command
# Download the current backup from each SBC via SCP
#

# import modules
import platform
import os
import sys
import logging
from pathlib import Path
import getpass
import csv
from datetime import date
from netmiko import ConnectHandler, file_transfer
import paramiko


# setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    filename="acmeBackup.log"
    )

# check what OS we are running on
platformType = platform.system()

# set some variables
dateToday = date.today().strftime("%m%d%Y").replace('-','')
homePath = str(Path.home() / "Downloads") + "/"
sbcBackupPath = "/code/bkups/"
# clientBackupPath = homePath

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

# display a text welcome message and prompt for the SBC ADMIN Password
# we are assuming all the SBCs use the same password.
try:
    print(welcomeMsg)
    sbcUsername = "admin"
    sbcPassword = getpass.getpass("Enter the SBC ADMIN account password: ")
except Exception as error:
    print("There was an error accepting your password", error)
else:
    print("Thank you")


# read a list of SBC IP Addresses to backup from sbc.txt
sbcIPAddressFile = open("sbc.txt")
sbcIPAddressList = sbcIPAddressFile.read().splitlines()



# create a file name for the backup file on the sbc
# backupFileName = deviceName + "ACMEBU" + dateToday + "Tool"


# define our blank connect profile
#acmeSBC = {}

####### Loop Should Start Here   #######



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


####### Loop Should End Here   #######


# print the output of the commands to the acmeBackup.log file
logging.info("Variable data:")
logging.info(dateToday)
logging.info(platformType)
logging.info(homePath)
logging.info(backupFileNameExt)
logging.info(sbcIPAddressList)

# disconnect the sessions
net_connect.disconnect()
sftpClient.close()
transportClient.close()

# and we're done. print a note saying so and remind where the backups are locally
print("\nThe backups have been completed. Find them in your downloads directory: " + str(homePath))
print("\nAll sessions have been closed. Have a nice day!\n\n\a")
