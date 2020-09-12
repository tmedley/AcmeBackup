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
from pathlib import Path
import getpass
import csv
from datetime import date
from netmiko import ConnectHandler, file_transfer
import paramiko
import os
import logging

# setup logging
logging.basicConfig(level=logging.)

# check what OS we are running on
platformType = platform.system()

# set some variables
dateToday = date.today().strftime("%m%d%y").replace('-','')
homePath = str(Path.home() / "Downloads") + "/"

# prompt for the SBC user Password
welcomeMsg = """
########################################

          MAXIMUS Telecom Team
        AcmePacket SBC Backup Tool

########################################

This tool will load a list of sbc's from
the sbc.csv file then ssh to each sbc
generate a backup and then download that
backup file.
"""

print(welcomeMsg)
sbcUsername = "admin"
sbcPassword = getpass.getpass("Enter the SBC admin account password: ")


# read sbc ip addresses and name from file sbc_ip_address.txt
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

# Define static devices
acmeSBC = {
    "device_type" : "linux",
    "ip" : "192.168.180.200",
    "username" : sbcUsername,
    "password" : sbcPassword,
}


# Connect to a device
net_connect = ConnectHandler(**acmeSBC)
net_connect.enable()


# tell the sbc to generate a new backup file
# filename format is: DC SBC_Name ACME BU DATE USER
try:
    acmeBackupCommand = net_connect.send_command("backup-config " + backupFileName + " running")
    output = net_connect.send_command("display-backups")
    print("a backup has been created on the SBC, with file name: " + backupFileName)
except:
    print(acmeSBC["host"] + " not connected")


print("source: " + sbcBackupFullPath)
print("destination: " + clientBackupFullPath)



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
transportClient = paramiko.Transport("192.168.180.200")
transportClient.connect(username = sbcUsername, password = sbcPassword)
sftpClient = paramiko.SFTPClient.from_transport(transportClient)
sftpClient.get(sbcBackupFullPath, clientBackupFullPath)



# print the output of the commands to the screen
print(dateToday)
print(sbcPassword)
print(platformType)
print(homePath)
print(backupFileName)
print(output)
print(ipAddressList)
print(deviceNameList)


# disconnect the sessions
net_connect.disconnect()
sftpClient.close()
transportClient.close()

print("Sessions are closed")
