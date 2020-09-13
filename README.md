# AcmeBackup

Acme Packet/Oracle SBC Backup script

A quick tool to reach out to several AcmePacket/Oracle SBCs to automate the process of backing them up. This script will parse a txt file to pull a list of SBCs to backup, SSH to each SBC, create a new backup file and then download the backup via SFTP to a local directory.

This was written for a specific set of SBCs that I help manage, When run, the script will prompt for the Admin password for the SBCs, it is assumed that all of the SBCs use the same Admin level password.  If not the script would need to be modified to prompt for a password for each SBC.

A TXT file is used to provide a list of SBC IP Addresses, one IP per line.

This is a quickly thrown together script, I am sure there are things I can improve on or do more efficiently. I might do those things over time.

I mainly used netmiko for the SSH and command parsing, it's overkill but makes this really easy. I used paramiko to handle SFTP get easily, since netmiko doesn't do that sort of thing.
