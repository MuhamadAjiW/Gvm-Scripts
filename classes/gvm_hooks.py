from flask import *
import os
import threading
from libraries import GVMLogger
from config import Config
from classes.gvm_report import GVMReport


class GVMHooks:
    def __init__(
        self,
        whitelist: bool = True,
        allowed_ips: list = ["127.0.0.1"],
        host: str = "127.0.0.1",
        port: int = 5000,
    ):
        self.allowed_ips = allowed_ips
        self.app = Flask(__name__)
        self.port = port
        self.host = host
        self.setup_routes()
        self.whitelist = whitelist

        self.__write_log = GVMLogger(__name__, Config.HOOKS_LOG_FILE).write_log

    def set_whitelist(self, status: bool):
        self.whitelist = status

    def set_allowed_ips(self, allowed_ips: list):
        self.allowed_ips = allowed_ips

    def setup_routes(self):
        @self.app.route("/")
        def test():
            if self.whitelist and (request.remote_addr not in self.allowed_ips):
                self.__write_log(
                    f"Refused connection from {request.remote_addr}", GVMLogger.WARN
                )
                abort(403)
            self.__write_log("Gvm hook is being tested")
            return "Flask hooks is running\n"

        @self.app.route("/api/report/latest")
        def latest_report():
            if self.whitelist and (request.remote_addr not in self.allowed_ips):
                self.__write_log(
                    f"Refused connection from {request.remote_addr}", GVMLogger.WARN
                )
                abort(403)

            self.__write_log("Gvm hook is called to ship latest report data")
            report = GVMReport(host_name=Config.HOST)
            thread = threading.Thread(
                target=report.ship_data, args=[f"{Config.CACHE_PATH}/temp"]
            )
            thread.start()

            return "Acknowledged\n"

    def run(self, **kwargs):
        self.app.run(host=self.host, port=self.port, **kwargs)
        self.__write_log(f"Gvm hooks running at http://{self.host}:{self.port}\n")

    def _load_allowed_ips(self, file_path: str):
        if not file_path or not os.path.isfile(file_path):
            return ["127.0.0.1"]

        allowed_ips = []
        try:
            with open(file_path, "r") as file:
                allowed_ips = [line.strip() for line in file if line.strip()]
        except Exception as e:
            self.__write_log(
                f"Error reading allowed IPs from file: {e}\n", GVMLogger.ERROR
            )
            allowed_ips = ["127.0.0.1"]

        return allowed_ips


if __name__ == "__main__":
    gvm_hooks = GVMHooks()
    gvm_hooks.set_whitelist(False)
    gvm_hooks.run()
