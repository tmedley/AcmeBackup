# AcmeBackup

Acme Packet/Oracle SBC Backup script

A quick tool to reach out to several AcmePacket/Oracle SBCs to automate the process of backing them up.
This script will parse a csv file to pull a list of SBCs to backup, then it will SSH to each SBC create
a new backup file and then download the backup viah SFTP to your local downloads directory.

This was written for a specific set of SBCs that I help manage, When run, the script will prompt for the Admin password for the SBCs, it is assumed that all of the SBCs use the same Admin level password.  If not the script would need to be modified to prompt for a password for each SBC.

A TXT file is used to provide a list of SBC IP Addresses, one IP per line.

This is a quickly thrown together script, I am sure there are things I can improve on or do more efficiently. I might do those things over time.

I mainly used netmiko for the SSH and command parsing, it's overkill but makes this really easy. I ran into issues using SCP in netmiko for the file transfer. The Acme SBCs seem like they support SCP, but I could not get it to connect, so I ended up adding paramiko since it handles SFTP easily.
