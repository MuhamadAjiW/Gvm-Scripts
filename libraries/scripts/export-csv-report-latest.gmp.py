# -*- coding: utf-8 -*-
# Copyright (C) 2019-2021 Greenbone Networks GmbH
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Based on other Greenbone scripts
#
# Martin Boller 2023-05-15
#
# run script with e.g. gvm-script --gmp-username username --gmp-password password socket list-reports.gmp.py All
#

from gvm.protocols.gmp import Gmp

from gvmtools.helper import Table

from argparse import ArgumentParser, Namespace, RawTextHelpFormatter

import sys
from base64 import b64decode
from pathlib import Path

HELP_TEXT = "This script exports the latest finished scan "


def get_latest_report_id(gmp: Gmp):
    response_xml = gmp.get_reports(
        ignore_pagination=True,
        details=True,
        filter_string="status=Done  and sort-reverse=modified  and rows=-1",
    )

    reports_xml = response_xml.xpath("report")
    return reports_xml[0].get("id")


def check_args(args):
    len_args = len(args.script) - 1
    if len_args < 1:
        message = """
        This script requests the given report and exports it as a csv 
        file locally. It requires one parameter after the script name.

        1. <file_name>     -- file name to save the csv in.
        
        Examples:
            $ gvm-script --gmp-username name --gmp-password pass \
ssh --hostname <gsm> scripts/export-csv-report.gmp.py <report_id> <csv_file>
            $ gvm-script --gmp-username admin --gmp-password '0f6fa69b-32bb-453a-9aa4-b8c9e56b3d00' socket export-csv-report.gmp.py ./test.csv
        """
        print(message)
        sys.exit()


def main(gmp: Gmp, args: Namespace) -> None:
    # check if report id and CSV filename are provided to the script
    # argv[0] contains the script name
    check_args(args)

    print("Exporting latest report.\n")

    report_id = get_latest_report_id(gmp)
    csv_filename = f"{args.argv[1]}.csv"

    csv_report_format_id = "c1645568-627a-11e3-a660-406186ea4fc5"

    response = gmp.get_report(
        report_id=report_id,
        report_format_id=csv_report_format_id,
        ignore_pagination=True,
        details=True,
    )

    report_element = response.find("report")
    # get the full content of the report element
    content = report_element.find("report_format").tail

    if not content:
        print(
            "Requested report is empty. Either the report does not contain any "
            " results or the necessary tools for creating the report are "
            "not installed.",
            file=sys.stderr,
        )
        sys.exit(1)

    # convert content to 8-bit ASCII bytes
    binary_base64_encoded_csv = content.encode("ascii")

    # decode base64
    binary_csv = b64decode(binary_base64_encoded_csv)

    # write to file and support ~ in filename path
    csv_path = Path(csv_filename).expanduser()

    csv_path.write_bytes(binary_csv)

    print("Done. CSV created: " + str(csv_path))


if __name__ == "__gmp__":
    main(gmp, args)
