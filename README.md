# add_service: python tool for simply adding startup item by systemd.

```bash
Python tool for simply adding startup item by systemd.

Install:
    pip install add_service

Usage:
    python -m add_service shell_file/cmd [--user root(default `whoami`)] [--name service_name] [--start]

    positional arguments:
        script       Executable file or cmd

    optional arguments:
    -h, --help   show this help message and exit
    -l, --ls     List all services created by add_service
    --user USER  User to exec script, default is `whoami`
    --name NAME  Service name
    --start      Start service immediately

Examples:
    python -m add_service ssh_nat.sh   # defaut service name is ssh_nat.service
    python -m add_service "`which python3` -m http.server 80" --user root --name http_server
```
**For example:** share directory "~/share" by python http.server when system startup.
```bash
user@host:~$ cd ~/share/
user@host:~/share$ python -m add_service "`which python3` -m http.server 80" --user root --name http_server
```
```
Below will write to "http_server.service"
--------------------

[Unit]
Description="http_server.service added by add_service: Namespace(name='http_server', script='/home/dl/miniconda3/bin/python3 -m http.server 80', user='root')"
After=network.service
[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/home/user/share
ExecStart=/usr/bin/python3 -m http.server 80
PrivateTmp=false
Restart=on-failure
[Install]
WantedBy=multi-user.target
    
--------------------
Need sudo to create: /etc/systemd/system/http_server.service
And exec `sudo systemctl enable http_server.service`
[sudo] password for user: 

Created symlink /etc/systemd/system/multi-user.target.wants/http_server.service → /etc/systemd/system/http_server.service.
Start service right now by manual:
	sudo systemctl start http_server.service
```

