# AcmeBackup

Acme Packet/Oracle SBC Backup script

A quick tool to reach out to several AcmePacket/Oracle SBCs to automate the process of backing them up.
This script will parse a csv file to pull a list of SBCs to backup, then it will SSH to each SBC create
a new backup file and then download the backup viah SFTP to your local downloads directory.

This was written for a specific set of SBCs that I help manage, When run, the script will prompt for the Admin password for the SBCs, it is assumed that all of the SBCs use the same Admin level password.  If not the script would need to be modified to prompt for a password for each SBC.

The CSV file contains two fields: IP_ADDRESS, HOSTNAME.  The Hostname field is used in the script for part of the file backup file nameing.  We use a naming convention:  

      XXX           XXX       ACME    BU        DDMMYY              XX                                      CULMGEPACMEBU122520TM
      Data Center   Project   ACME    Back Up   Day Month Year      Initials of who did the Back Up
      
This is a quickly thrown together script, I am sure there are things I can improve on or do more efficiently. I might do those things over time.
