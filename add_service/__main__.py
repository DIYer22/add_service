#!/usr/bin/env python3
__version__ = "0.2.1"
__description__ = "CLI tool for simply adding startup item by systemd."
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


added_by_add_service = "added by add_service"


def list_all_services():
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


def main(argv=None):
    if argv is None:
        argv = sys.argv
    prefix = "" if os.system("which sudo>/dev/zero") else "sudo "
    if "-l" in argv or "--ls" in argv or ("ls" in argv and len(argv) == 2):
        print(list_all_services())
        exit(0)

    if "--rm" in argv:
        service_names = argv[argv.index("--rm") + 1 :]
        for service_name in service_names:
            service_name = service_name.replace(".service", "") + ".service"
            service_path = "/etc/systemd/system/{service_name}".format(
                service_name=service_name
            )
            assert os.path.isfile(service_path), service_path
            cmd = '{prefix}systemctl stop "{service_name}"; {prefix}systemctl disable "{service_name}"; {prefix}rm "{service_path}"'.format(
                prefix=prefix, service_name=service_name, service_path=service_path
            )
            print(
                "Remove {service_name} by cmd:\n\t{cmd}".format(
                    service_name=service_name, cmd=cmd
                )
            )
            assert not os.system(cmd), cmd
        exit(0)

    if "-h" in argv or "--help" in argv:
        description = doc + "\n" + list_all_services()
    else:
        description = doc

    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("script", type=str, help="Executable file or cmd")
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
        help="User to exec script, default is `whoami`",
    )
    parser.add_argument(
        "--name", default=None, help="Service name, default add_service0.service"
    )
    parser.add_argument(
        "--start", action="store_true", help="Start service immediately"
    )

    args = parser.parse_args()

    if os.path.isfile(args.script):
        args.script = os.path.abspath(args.script)
        name = filename(args.script)
        assert os.access(
            args.script, os.X_OK
        ), 'Please "chmod +x {args_script}"'.format(args_script=args.script)
        if args.script.endswith(".sh"):
            _msg = '`.sh` file should start with "#!/usr/bin/env bash"'
            assert open(args.script).read().strip().startswith("#!"), _msg
    else:
        # Get abspath of exe
        exe_name = args.script.split(" ")[0]
        if "/" not in exe_name and not os.system("which %s>/dev/zero" % exe_name):
            exe_path = execmd("which %s" % exe_name).strip()
            args.script = args.script.replace(exe_name, '"%s"' % exe_path, 1)
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

    assert not os.path.isfile(service_path), service_path
    service_str = """
[Unit]
Description="{service_name} {added_by_add_service}: {args}"
After=network.service
[Service]
Type=simple
User={args_user}
Group={group}
WorkingDirectory={dir_path}
ExecStart={args_script}
PrivateTmp=false
Restart=on-failure
[Install]
WantedBy=multi-user.target
    """.format(
        added_by_add_service=added_by_add_service,
        service_name=service_name,
        args=args,
        args_user=args.user,
        group=group,
        dir_path=dir_path,
        args_script=args.script,
    )
    tmp_path = "/tmp/" + service_path.replace("/", "-")
    with open(tmp_path, "w") as f:
        f.write(service_str)
    print('Below will write to "{service_name}"'.format(service_name=service_name))
    print("-" * 20)
    print(service_str)
    print("-" * 20)

    print(
        "Need {prefix}to create: {service_path}".format(
            prefix=prefix, service_path=service_path
        )
    )
    print(
        "And exec `{prefix}systemctl enable {service_name}`".format(
            prefix=prefix, service_name=service_name
        )
    )
    cmd = """{prefix}mv "{tmp_path}" "{service_path}" && {prefix}systemctl enable {service_name}""".format(
        prefix=prefix,
        service_name=service_name,
        tmp_path=tmp_path,
        service_path=service_path,
    )

    start_cmd = "{prefix}systemctl start {service_name}".format(
        prefix=prefix, service_name=service_name
    )
    if args.start:
        cmd += " && " + start_cmd

    print("Execute cmd:")
    print("\t" + cmd)
    assert not os.system(cmd)

    if not args.start:
        print("Start service right now by manual:")
        print("\t" + start_cmd)


if __name__ == "__main__":
    # Test CMD:
    # python -m add_service "ssh 127.0.0.1 -L 0.0.0.0:8080:al.diyer22.com:9000 -N" --user root --name ssh_test --start
    # python2 -m add_service "python2 -m SimpleHTTPServer 80" --user root --name py2_server --start
    # python2 -m add_service --rm ssh_test
    # python -m add_service --rm py2_server
    main()
