import pandas as pd
import json
import subprocess
from libraries import GVMLogger
from datetime import datetime
from libraries.common import convert_floats_to_ints
from config import Config


class GVMReport:
    def __init__(
        self,
        openvas_addr: str = "127.0.0.1",
        host_name: str = "root",
        program_name: str = "openvas",
    ):
        self.server_addr = openvas_addr
        self.host_name = host_name
        self.program_name = program_name

        self.__write_log = GVMLogger(__name__, Config.REPORT_LOG_FILE).write_log

    def process_data(self, input_file: str) -> list:
        self.__write_log("Processing data", GVMLogger.INFO)
        data = pd.read_csv(input_file)
        final_data = []

        for index, row in data.iterrows():
            data_json = row.to_dict()

            for key in data_json:
                value = data_json[key]
                if pd.isna(value):
                    data_json[key] = None
                elif isinstance(value, str):
                    data_json[key] = value.strip()

            if data_json.get("CERTs") is not None:
                data_json["CERTs"] = data_json["CERTs"].split(sep=",")
            else:
                data_json["CERTs"] = [""]

            if data_json.get("Other References") is not None:
                data_json["Other References"] = data_json["Other References"].split(
                    sep=","
                )
            else:
                data_json["Other References"] = []

            if data_json.get("BIDs") is not None:
                data_json["BIDs"] = data_json["BIDs"].split(sep=",")
            else:
                data_json["BIDs"] = [""]

            if data_json.get("CVEs") is not None:
                data_json["CVEs"] = data_json["CVEs"].split(sep=",")
            else:
                data_json["CVEs"] = [""]

            if data_json.get("Hostname") is None:
                data_json["Hostname"] = ""

            if data_json.get("Impact") is None:
                data_json["Impact"] = ""

            if data_json.get("Affected Software/OS") is None:
                data_json["Affected Software/OS"] = ""

            if data_json.get("Product Detection Result") is None:
                data_json["Product Detection Result"] = ""

            if data_json.get("Vulnerability Insight") is None:
                data_json["Vulnerability Insight"] = ""

            if data_json.get("Port Protocol") is None:
                data_json["Port Protocol"] = ""

            data_json = convert_floats_to_ints(data_json)

            certs = data_json["CERTs"]
            cvss = data_json["CVEs"]
            bids = data_json["BIDs"]

            for cert in certs:
                temp_json = data_json.copy()
                temp_json["CERTs"] = cert
                temp_json["CVEs"] = ""
                temp_json["BIDs"] = ""
                final_data.append(temp_json)

            for cve in cvss:
                temp_json = data_json.copy()
                temp_json["CERTs"] = ""
                temp_json["CVEs"] = cve
                temp_json["BIDs"] = ""
                final_data.append(temp_json)

            for bid in bids:
                temp_json = data_json.copy()
                temp_json["CERTs"] = ""
                temp_json["CVEs"] = ""
                temp_json["BIDs"] = bid
                final_data.append(temp_json)

        self.__write_log("Processing data completed", GVMLogger.INFO)
        return final_data

    def output_data(
        self, processed_data: list, output_file: str = "./output", mode: str = "w"
    ) -> list:
        self.__write_log("Outputting data", GVMLogger.INFO)
        with open(output_file, mode) as f:
            for entry in processed_data:
                current_time = datetime.now().strftime("%b %d %H:%M:%S")
                prefix = f"{current_time} {self.host_name} {self.program_name}: "
                json_line = json.dumps(entry)
                f.write(f"{prefix}{json_line}\n")
        self.__write_log("Outputting data completed", GVMLogger.INFO)

    def ingest_data(self, output_file) -> str:
        self.__write_log("Ingesting data", GVMLogger.INFO)
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
            f"{Config.SCRIPTS_PATH}/export-csv-report-latest.gmp.py",
            output_file,
        ]
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        self.__write_log("Ingesting data completed", GVMLogger.INFO)

        return f"{output_file}.csv"

    def ship_data(self, output_file: str):
        try:
            self.__write_log("Shipping data", GVMLogger.INFO)
            temp_file = f"{Config.CACHE_PATH}/temp"
            temp_file = self.ingest_data(temp_file)
            list = self.process_data(temp_file)
            self.output_data(list, output_file)
            self.output_data(list, Config.OUTPUT_PATH, mode="a")
            self.__write_log("Shipping data completed", GVMLogger.INFO)

        except Exception as e:
            self.__write_log(e.with_traceback, GVMLogger.ERROR)
