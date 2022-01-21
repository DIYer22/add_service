# add_service

```
Python tool for quickly adding startup item by systemd.

Install:
    pip install add_service

Usage:
    python -m add_service [shell_file/cmd] [user (default `whoami`)]

Examples:
    python -m add_service ssh_nat.sh
    python -m add_service "`which python3` -m http.server 80" root
```