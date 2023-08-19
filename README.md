# 🚀`add_service`: Effortlessly create and manage systemd startups with just one command.

```bash
Install:
    pip install add_service  # support both python2/python3

Examples:
    add_service "python3 -m http.server 80" --user root --name http_server --start
    python -m add_service ssh_nat.sh   # defaut service name is ssh_nat.service

Usage:
    add_service shell_file/cmd [--user root(default `whoami`)] [--name service_name] [--start]

    positional arguments:
      executable   Command or any executable file(`bin`, `.sh`, `.py`, `.js`)

    optional arguments:
    --user USER    User to execute, default is `whoami`
    --name NAME    Service name, default add_service0.service
    --start        Start service immediately
    --envs ENVS    List of environment variable names to save (e.g. "PATH,DISPLAY")
    --clone-envs   Clone all environment variables in the current shell
    -l, --ls       List all services created by add_service
    --rm NAME      Remove the service created by add_service
    -h, --help     show this help message
```
**For example:** share directory `~/share` by python3 `http.server` when system startup.  
```bash
user@host:~$ cd ~/share/
user@host:~/share$ add_service "python3 -m http.server 80" --user root --name http_server --start
```

```
Below will write to "/etc/systemd/system/http_server.service"
--------------------

[Unit]
Description="http_server.service added by add_service: add_service "python3 -m http.server 80" --user root --name http_server --start"
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
Need sudo to create and enable service, the execute commands:
        sudo mv /tmp/http_server.tmp.service /etc/systemd/system/http_server.service &&
        sudo systemctl enable http_server.service &&
        sudo systemctl start http_server.service
[sudo] password for user: 
Created symlink /etc/systemd/system/multi-user.target.wants/http_server.service → /etc/systemd/system/http_server.service.

View Service working status and log by:
        sudo systemctl status tmp_test_add_service.service
        sudo journalctl -f -u tmp_test_add_service.service
```

