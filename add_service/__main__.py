#!/usr/bin/env python3
__version__ = "0.0.4"
__description__ = "Python tool for simply adding startup item by systemd."
__license__ = "MIT"
__author__ = "DIYer22"
__author_email__ = "ylxx@live.com"
__maintainer__ = "DIYer22"
__maintainer_email__ = "ylxx@live.com"
__github_username__ = "DIYer22"
__url__ = "https://github.com/DIYer22/add_service"
__support__ = "https://github.com/DIYer22/add_service/issues"
__classifiers__ = [
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

import os
import sys

doc = f"""
{__description__}

Install:
    pip install add_service

Usage:
    python -m add_service [shell_file/cmd] [user (default `whoami`)]

Examples:
    python -m add_service ssh_nat.sh
    python -m add_service "`which python3` -m http.server 80" root
"""


def execmd(cmd):
    """
    execuld cmd and reutrn str(stdout)
    """
    with os.popen(cmd) as stream:
        stream = stream._stream
        s = stream.read()
    return s.strip()


def get_group(user):
    return execmd(f"id -Gn {user}").split()[0]


def filename(path):
    filen = name = os.path.basename(path)
    if "." in name:
        filen = name[: name.rindex(".")]
    return filen




if __name__ == "__main__":
    args = sys.argv[1:]
    
    if len(args) == 0:
        print(doc)
        exit(1)
    elif len(args) == 1:
        args.append(execmd("whoami"))
    # assert os.path.isfile(exec_start)
    # assert open(exec_start).read().strip().startswith("#!")
    
    exec_start, user = args
    if os.path.isfile(exec_start):
        exec_start = os.path.abspath(exec_start)
        name = filename(exec_start)
        assert os.access(exec_start, os.X_OK), f'Please "chmod +x {exec_start}"'
        if exec_start.endswith(".sh"):
            _msg = '`.sh` file should start with "#!/usr/bin/env bash"'
            assert open(exec_start).read().strip().startswith("#!"), _msg
    else:
    
        for idx in range(9999):
            name = "add_service" + str(idx)
            service_path = f"/etc/systemd/system/{name}.service"
            if not os.path.isfile(service_path):
                break
    
    dir_path = os.path.abspath(".")
    group = get_group(user)
    
    service_path = f"/etc/systemd/system/{name}.service"
    service_name = os.path.basename(service_path)
    
    assert not os.path.isfile(service_path), service_path
    
    
    service_str = f"""
    [Unit]
    Description="{service_name} added by add_service: {args}"
    After=network.service
    [Service]
    Type=simple
    User={user}
    Group={group}
    WorkingDirectory={dir_path}
    ExecStart={exec_start}
    PrivateTmp=true
    Restart=on-failure
    [Install]
    WantedBy=multi-user.target
    """
    tmp_path = "/tmp/" + service_path.replace("/", "-")
    with open(tmp_path, "w") as f:
        f.write(service_str)
    print("-" * 20)
    print(service_str)
    print("-" * 20)

    print(f"Need sudo to create: {service_path}")
    print(f"And exec `sudo systemctl enable {service_name}`")
    cmd = f"""sudo mv "{tmp_path}" "{service_path}" && sudo systemctl enable {service_name}"""
    # print("Run cmd:")
    # print("\t"+cmd)
    assert not os.system(cmd)
    print("Start service right now by manual:")
    print(f"\tsudo systemctl start {service_name}")
