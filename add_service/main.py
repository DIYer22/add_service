#!/usr/bin/env python3
__version__ = "1.1.0"
__description__ = (
    "Effortlessly create and manage systemd startups with just one command."
)
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
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

import os
import sys
import glob
import argparse

doc = """
{__description__}

Install:
    pip install add_service

Usage:
    add_service shell_file/cmd [--user root(default `whoami`)] [--name service_name] [--start]

Examples:
    add_service "`which python3` -m http.server 80" --user root --name http_server
    python -m add_service ssh_nat.sh   # defaut service name is ssh_nat.service

See: 
    https://github.com/DIYer22/add_service
""".format(
    __description__=__description__
)


added_by_add_service = "added by add_service"
prefix = "" if os.system("which sudo>/dev/zero") else "sudo "


def execmd(cmd):
    """
    Execute cmd and return str(stdout)
    """
    from subprocess import Popen, PIPE

    process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, _ = process.communicate()

    if sys.version_info[0] < 3:
        return stdout.strip()
    else:
        return stdout.decode().strip()


def get_group(user):
    return execmd("id -Gn {user}".format(user=user)).split()[0]


def filename(path):
    filen = name = os.path.basename(path)
    if "." in name:
        filen = name[: name.rindex(".")]
    return filen


def generate_environment_lines(envs):
    def escape_value(value):
        return value.replace("'", "''").replace('"', '\\"')

    environment_lines = []

    for key, value in envs.items():
        escaped_value = escape_value(value)
        environment_line = f'Environment="{key}={escaped_value}"'
        environment_lines.append(environment_line)

    return "\n".join(environment_lines)


def list_services():
    str = ""
    service_paths = sorted(glob.glob("/etc/systemd/system/*.service"))
    for service_path in service_paths:
        try:
            if added_by_add_service in open(service_path).read():
                str += "\n\t{base_service_path}\t{service_path}".format(
                    base_service_path=os.path.basename(service_path),
                    service_path=service_path,
                )
        except:
            pass
    str = "Services created by add_service:" + (str if str else " null")
    return str


def remove_services(service_names):
    for service_name in service_names:
        service_name = service_name.replace(".service", "") + ".service"
        service_path = "/etc/systemd/system/{service_name}".format(
            service_name=service_name
        )
        assert os.path.isfile(service_path), service_path
        cmd = '{prefix}systemctl stop "{service_name}";\n\t{prefix}systemctl disable "{service_name}";\n\t{prefix}rm "{service_path}";'.format(
            prefix=prefix, service_name=service_name, service_path=service_path
        )
        print(
            "Remove {service_name} by cmd:\n\t{cmd}".format(
                service_name=service_name, cmd=cmd
            )
        )
        assert not os.system(cmd), cmd


def main(argv=None):
    if argv is None:
        argv = sys.argv
    if "-l" in argv or "--ls" in argv or ("ls" in argv and len(argv) == 2):
        print(list_services())
        exit(0)

    if "-v" in argv or "--version" in argv:
        print("add_service v" + __version__)
        print("License:", __license__)
        print("Path:", __file__)
        print("Url:", __url__)
        exit(0)

    if "--rm" in argv:
        service_names = argv[argv.index("--rm") + 1 :]
        remove_services(service_names)
        exit(0)

    if "-h" in argv or "--help" in argv:
        description = doc + "\n" + list_services()
    else:
        description = doc

    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("executable", type=str, help="Executable file or command line")
    parser.add_argument(
        "-l",
        "--ls",
        action="store_true",
        help="List all services created by add_service",
    )
    parser.add_argument(
        "--rm",
        metavar="NAME",
        default=None,
        help="Remove the service created by add_service",
    )
    parser.add_argument(
        "--user",
        default=execmd("whoami"),
        help="User to exec executable, default is `whoami`",
    )
    parser.add_argument(
        "--name", default=None, help="Service name, default add_service0.service"
    )
    parser.add_argument(
        "--start", action="store_true", help="Start service immediately"
    )
    parser.add_argument(
        "-e",
        "--envs",
        default=None,
        help='List of environment variable names to save, using comma to split (e.g. "PATH,DISPLAY")',
    )
    parser.add_argument(
        "-c",
        "--clone-envs",
        action="store_true",
        help="Clone all environment variables in the current shell",
    )
    parser.add_argument(
        "-v", "--version", action="store_true", help="Version of add_service"
    )

    args = parser.parse_args()
    args_raw_str = 'add_service "%s" ' % argv[1] + str(" ".join(argv[2:]))
    args_raw_str = args_raw_str.replace("\n", "↳")

    # First argument of unit's"ExecStart=" should be abspath
    if os.path.isfile(args.executable):
        # match: "path/to/shell.sh" or "path/to/script.py"
        args.executable = os.path.abspath(args.executable)
        name = filename(args.executable)
        assert os.access(
            args.executable, os.X_OK
        ), 'Please "chmod +x {args_script}"'.format(args_script=args.executable)
        if args.executable.endswith(".sh"):
            _msg = '`.sh` file should start with "#!/usr/bin/env bash"'
            assert open(args.executable).read().strip().startswith("#!"), _msg
    else:
        # Get abspath of exe
        exe_name = args.executable.split(" ")[0]
        if "/" not in exe_name and not os.system("which %s>/dev/zero" % exe_name):
            # match: "exe foo --arg bar"
            exe_path = execmd("which %s" % exe_name).strip()
            args.executable = args.executable.replace(exe_name, '"%s"' % exe_path, 1)
        elif "/" in exe_name and os.path.isfile(exe_name) and "/" != exe_name[:1]:
            # match: "./exe foo --arg bar"
            exe_path = os.path.abspath(args.executable)
            args.executable = args.executable.replace(exe_name, '"%s"' % exe_path, 1)
        # Get default service name
        for idx in range(9999):
            name = "add_service" + str(idx)
            service_path = "/etc/systemd/system/{name}.service".format(name=name)
            if not os.path.isfile(service_path):
                break
    name = args.name or name

    dir_path = os.path.abspath(".")
    group = get_group(args.user)

    service_path = "/etc/systemd/system/{name}.service".format(name=name)
    service_name = os.path.basename(service_path)
    assert not os.path.isfile(service_path), "Service file exists: " + service_path

    # envs
    envs = {}
    if args.clone_envs:
        IGNORE_CLONE_NAMES = [
            "LC_PAPER",
            "LC_MONETARY",
            "HOME",
            "LC_IDENTIFICATION",
            "LC_TELEPHONE",
            "LC_MEASUREMENT",
            "LANG",
            "LOGNAME",
            "LC_NUMERIC",
            "LC_ADDRESS",
            "LC_NAME",
            "USER",
            "LC_TIME",
        ]  # Provide by systemd default
        IGNORE_CLONE_NAMES += ["LS_COLORS"]  # Long and useless
        envs = dict(os.environ)
        for key in list(envs):
            if key in IGNORE_CLONE_NAMES:
                envs.pop(key)
            if key.startswith("XDG_") or key.startswith("GNOME_"):
                envs.pop(key)  # Useless, GUI related
    if args.envs:
        for env_name in args.envs.split(","):
            env_name = env_name.strip()
            assert env_name in os.environ, 'VARNAME: "%s" not in Environment' % env_name
            envs[env_name] = os.environ[env_name]
    envs_str = generate_environment_lines(envs)
    service_str = """[Unit]
Description="{service_name} {added_by_add_service}: {args_raw_str}"
After=network.service
[Service]
Type=simple
User={args_user}
Group={group}
WorkingDirectory={dir_path}
ExecStart={args_script}
PrivateTmp=false
Restart=on-failure
{envs_str}
[Install]
WantedBy=multi-user.target
""".format(
        added_by_add_service=added_by_add_service,
        service_name=service_name,
        args_raw_str=args_raw_str,
        args_user=args.user,
        group=group,
        dir_path=dir_path,
        args_script=args.executable,
        envs_str=envs_str,
    )
    tmp_path = "/tmp/%s.tmp.service" % name
    with open(tmp_path, "w") as f:
        f.write(service_str)
    print('Below will write to "{service_path}"'.format(service_path=service_path))
    print("-" * 20)
    print(service_str)
    print("-" * 20)

    cmd = """{prefix}mv "{tmp_path}" "{service_path}" &&\n\t{prefix}systemctl enable {service_name}""".format(
        prefix=prefix,
        service_name=service_name,
        tmp_path=tmp_path,
        service_path=service_path,
    )

    start_cmd = "{prefix}systemctl start {service_name}".format(
        prefix=prefix, service_name=service_name
    )
    status_cmd = "{prefix}systemctl status {service_name}".format(
        prefix=prefix, service_name=service_name
    )
    # start_cmd = start_cmd + " &&\n\t" + status_cmd
    if args.start:
        cmd += " &&\n\t" + start_cmd

    print(
        "Need {prefix}to create and enable service, the execute commands:".format(
            prefix=prefix
        )
    )
    print("\t" + cmd)
    assert not os.system(cmd)
    print()
    if not args.start:
        print("Start service by manual:")
        print("\t" + start_cmd)
    else:
        print("View Service working status and log by:")
        print("\t" + status_cmd)
        print(
            "\t"
            + "{prefix}journalctl -f -u {service_name}".format(
                prefix=prefix, service_name=service_name
            )
        )


if __name__ == "__main__":
    # Test CMD:
    # python -m add_service "ssh 127.0.0.1 -L 0.0.0.0:8080:al.diyer22.com:9000 -N" --user root --name ssh_test --start
    # python2 -m add_service "python2 -m SimpleHTTPServer 80" --user root --name py2_server --start
    # python2 -m add_service --rm ssh_test
    # python -m add_service --rm py2_server
    main()
