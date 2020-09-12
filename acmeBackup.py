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
dateToday = date.today().strftime("%m%d%y").replace('-','')
homePath = str(Path.home() / "Downloads") + "/"

# display a text welcome message and prompt for the SBC user Password
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

print(welcomeMsg)
sbcUsername = "admin"
sbcPassword = getpass.getpass("Enter the SBC admin account password: ")


# read sbc ip addresses and name from file sbc_ip_address.csv
with open("sbc_ip_addresses.csv") as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    ipAddressList = []
    deviceNameList = []
    for row in readCSV:
        ipAddress = row[0]
        deviceName = row[1]

        ipAddressList.append(ipAddress)
        deviceNameList.append(deviceName)




# create a file name for the backup file on the sbc
backupFileName = deviceName + "ACMEBU" + dateToday + "Tool"
backupFileNameExt = backupFileName + ".gz"
sbcBackupFullPath = "/code/bkups/" + backupFileNameExt
clientBackupFullPath = homePath + backupFileNameExt

# define our blank connect profile
acmeSBC = {}

####### Loop Should Start Here   #######

numberOfSBCs = len(ipAddressList)
i = 0

while i < numberOfSBCs:

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

        print(net_connect.find_prompt())
        # tell the sbc to generate a new backup file
        # filename format is: DC SBC_Name ACME BU DATE USER

        acmeBackupCommand = net_connect.send_command("backup-config " + backupFileName + " running")
        output = net_connect.send_command("display-backups")
    except:
        print("\nFailed to connect to: " + str(ipAddress))
        net_connect.disconnect()
        sys.exit(1)



        # get backup file via netmiko scp (didnt seems to work)
        # transferDir = "get"

        # transferBackup = file_transfer(
        # net_connect,
        # source_file=sbcBackupFullPath,
        # dest_file=backupFileNameExt,
        # direction=transferDir,
        # file_system=homePath,
        # )

        # get backup file via SFTP
        # privatekeyfile = os.path.expanduser('~/.ssh')
        # myKey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    try:
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

    i += 1

####### Loop Should End Here   #######


# print the output of the commands to the acmeBackup.log file
logging.info("Variable data:")
logging.info(dateToday)
logging.info(platformType)
logging.info(homePath)
logging.info(backupFileName)
logging.info(ipAddressList)
logging.info(deviceNameList)

# disconnect the sessions
net_connect.disconnect()
sftpClient.close()
transportClient.close()

# and we're done. print a note saying so and remind where the backups are locally
print("\nThe backups have been completed. Find them in your downloads directory: " + str(homePath))
print("\nAll sessions have been closed. Have a nice day!\n\n\a")
