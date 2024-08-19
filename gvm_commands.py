import argparse
import os
import subprocess
import sys
from config import Config
from classes.gvm_hooks import GVMHooks
from libraries.common import load_allowed_ips, is_root


global app
gvm_hooks_instance = GVMHooks(allowed_ips=load_allowed_ips(Config.ALLOWED_IP_FILE))
app = gvm_hooks_instance.app

if not is_root():
    print("Script must be run as root")
    sys.exit(1)


def start_server():
    if os.path.exists(Config.PID_FILE):
        print(
            "Server is already running (PID file exists, make sure to kill the process and not just deleting the PID file)."
        )
        sys.exit(1)

    with open(Config.LOG_FILE, "a") as log_file:
        process = subprocess.Popen(
            [
                "nohup",
                "gunicorn",
                "-b",
                f"{Config.HOST}:{Config.PORT}",
                "gvm_commands:app",
            ],
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )

    with open(Config.PID_FILE, "w") as pid_file:
        pid_file.write(str(process.pid))

    print(f"Server started with PID {process.pid}, check logs at {Config.LOG_FILE}")


def stop_server():
    if not os.path.exists(Config.PID_FILE):
        print("Server is not running.")
        sys.exit(1)

    with open(Config.PID_FILE, "r") as pid_file:
        pid = int(pid_file.read().strip())

    try:
        os.kill(pid, 15)  # Send SIGTERM
        print(f"Server stopped with PID {pid}")
    except OSError as e:
        print(f"Error stopping server: {e}")
        sys.exit(1)
    finally:
        os.remove(Config.PID_FILE)


def main():
    parser = argparse.ArgumentParser(description="Controller for gvm")
    parser.add_argument(
        "action",
        help="Action to perform",
    )
    parser.add_argument("args", nargs="*", help="Additional arguments to pass")

    args = parser.parse_args()

    if args.action == "start_hooks":
        start_server()
    elif args.action == "stop_hooks":
        stop_server()
    elif args.action == "reload_hooks":
        stop_server()
        start_server()
    else:
        try:
            command = [
                "sudo",
                "-u",
                Config.ALT_USER,
                "gvm-script",
                "--gmp-username",
                Config.USERNAME,
                "--gmp-password",
                Config.PASSWORD,
                "socket",
                f"{Config.SCRIPTS_PATH}/{args.action}",
            ] + args.args
            result = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            print("Standard Output:")
            print(result.stdout)

            print("Standard Error:")
            print(result.stderr)

            if result.returncode != 0:
                raise Exception(
                    f"Command '{args.action}' failed with exit code {result.returncode}"
                )

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
