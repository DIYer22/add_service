#!/usr/bin/env python3
__version__ = "0.1.2"
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
import glob
import argparse

doc = f"""
{__description__}

Install:
    pip install add_service

Usage:
    python -m add_service shell_file/cmd [--user root(default `whoami`)] [--name service_name] [--start]

Examples:
    python -m add_service ssh_nat.sh   # defaut service name is ssh_nat.service
    python -m add_service "`which python3` -m http.server 80" --user root --name http_server

See: 
    https://github.com/DIYer22/add_service
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


added_by_add_service = "added by add_service"


def list_all_services():
    str = ""
    service_paths = sorted(glob.glob("/etc/systemd/system/*.service"))
    for service_path in service_paths:
        try:
            if added_by_add_service in open(service_path).read():
                str += f"\n\t{os.path.basename(service_path)}\t{service_path}"
        except:
            pass
    str = "Services created by add_service:\n" + (str if str else "\tnull")
    return str


if __name__ == "__main__":
    if (
        "-l" in sys.argv
        or "--ls" in sys.argv
        or ("ls" in sys.argv and len(sys.argv) == 2)
    ):
        print(list_all_services())
        exit(0)
    if "-h" in sys.argv or "--help" in sys.argv:
        doc = doc + "\n" + list_all_services()

    parser = argparse.ArgumentParser(
        description=doc, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("script", type=str, help="Executable file or cmd")
    parser.add_argument(
        "-l",
        "--ls",
        action="store_true",
        help="List all services created by add_service",
    )
    parser.add_argument(
        "--user",
        default=execmd("whoami"),
        help="User to exec script, default is `whoami`",
    )
    parser.add_argument("--name", default=None, help="Service name")
    parser.add_argument(
        "--start", action="store_true", help="Start service immediately"
    )

    args = parser.parse_args()

    if os.path.isfile(args.script):
        args.script = os.path.abspath(args.script)
        name = filename(args.script)
        assert os.access(args.script, os.X_OK), f'Please "chmod +x {args.script}"'
        if args.script.endswith(".sh"):
            _msg = '`.sh` file should start with "#!/usr/bin/env bash"'
            assert open(args.script).read().strip().startswith("#!"), _msg
    else:
        assert not args.script.startswith("./"), "Executable path is not absolute path!"

        for idx in range(9999):
            name = "add_service" + str(idx)
            service_path = f"/etc/systemd/system/{name}.service"
            if not os.path.isfile(service_path):
                break
    name = args.name or name

    dir_path = os.path.abspath(".")
    group = get_group(args.user)

    service_path = f"/etc/systemd/system/{name}.service"
    service_name = os.path.basename(service_path)

    assert not os.path.isfile(service_path), service_path
    service_str = f"""
[Unit]
Description="{service_name} {added_by_add_service}: {args}"
After=network.service
[Service]
Type=simple
User={args.user}
Group={group}
WorkingDirectory={dir_path}
ExecStart={args.script}
PrivateTmp=false
Restart=on-failure
[Install]
WantedBy=multi-user.target
    """
    tmp_path = "/tmp/" + service_path.replace("/", "-")
    with open(tmp_path, "w") as f:
        f.write(service_str)
    print(f'Below will write to "{service_name}"')
    print("-" * 20)
    print(service_str)
    print("-" * 20)

    print(f"Need sudo to create: {service_path}")
    print(f"And exec `sudo systemctl enable {service_name}`")
    cmd = f"""sudo mv "{tmp_path}" "{service_path}" && sudo systemctl enable {service_name}"""

    start_cmd = f"sudo systemctl start {service_name}"
    if args.start:
        cmd += " && " + start_cmd

    print("Execute cmd:")
    print("\t" + cmd)
    assert not os.system(cmd)

    if not args.start:
        print("Start service right now by manual:")
        print(f"\t{start_cmd}")
