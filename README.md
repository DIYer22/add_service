# add_service: python tool for simply adding startup item by systemd.

```bash
Python tool for simply adding startup item by systemd.

Install:
    pip install add_service

Usage:
    python -m add_service [shell_file/cmd] [user (default `whoami`)]

Examples:
    python -m add_service ssh_nat.sh   # service name is ssh_nat.service
    python -m add_service "`which python3` -m http.server 80" root
    # service name is add_service0.service
```
**For example:** share directory "~/share" by python http.server when system startup.
```bash
user@host:~$ cd share/
user@host:~/share$ python -m add_service "`which python3` -m http.server 80" root
```
```
Below will write to "add_service0.service"
--------------------

[Unit]
Description="add_service0.service added by add_service: ['/usr/bin/python3 -m http.server 80', 'root']"
After=network.service
[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/home/user/share
ExecStart=/usr/bin/python3 -m http.server 80
PrivateTmp=true
Restart=on-failure
[Install]
WantedBy=multi-user.target
    
--------------------
Need sudo to create: /etc/systemd/system/add_service0.service
And exec `sudo systemctl enable add_service0.service`
[sudo] password for user: 

Created symlink /etc/systemd/system/multi-user.target.wants/add_service0.service → /etc/systemd/system/add_service0.service.
Start service right now by manual:
	sudo systemctl start add_service0.service
```

