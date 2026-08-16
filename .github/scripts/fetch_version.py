"""
Steps:
- goto: https://hub.spigotmc.org/versions/
- copy/paste the list in the "txt" variable underneath.
- run the script
- copy/paste the output in the "build_remapped_jars.py" script
"""
import json
import re
from pathlib import Path
from pprint import pprint

import requests

version_url = "https://hub.spigotmc.org/versions/"

txt = """
1.10.2.json                                        10-Dec-2021 01:54                 325
1.10.json                                          10-Dec-2021 01:54                 325
1.11.1.json                                        10-Dec-2021 02:02                 327
1.11.2.json                                        10-Dec-2021 02:02                 327
1.11.json                                          19-Dec-2016 12:14                 325
1.12.1.json                                        29-Aug-2018 23:54                 352
1.12.2.json                                        10-Dec-2021 01:31                 354
1.12.json                                          29-Aug-2018 23:56                 352
1.13-pre7.json                                     21-Jul-2018 04:58                 325
1.13.1.json                                        22-Oct-2018 19:00                 352
1.13.2.json                                        10-Dec-2021 01:31                 354
1.13.json                                          29-Aug-2018 23:54                 352
1.14-pre5.json                                     25-Apr-2019 00:20                 352
1.14.1.json                                        27-May-2019 02:27                 353
1.14.2.json                                        21-Jun-2019 09:57                 353
1.14.3-pre4.json                                   23-Jun-2019 01:05                 353
1.14.3.json                                        19-Jul-2019 23:04                 353
1.14.4.json                                        10-Dec-2021 01:31                 355
1.14.json                                          13-May-2019 22:53                 353
1.15.1.json                                        21-Jan-2020 03:40                 353
1.15.2.json                                        10-Dec-2021 01:31                 355
1.15.json                                          17-Dec-2019 21:19                 353
1.16.1.json                                        11-Aug-2020 07:40                 353
1.16.2.json                                        10-Sep-2020 20:55                 353
1.16.3.json                                        25-Oct-2020 07:17                 353
1.16.4.json                                        14-Jan-2021 22:05                 353
1.16.5.json                                        10-Dec-2021 01:31                 355
1.17.1.json                                        10-Dec-2021 01:32                 355
1.17.json                                          06-Jul-2021 12:21                 353
1.18-pre5.json                                     23-Nov-2021 22:37                 353
1.18-pre8.json                                     25-Nov-2021 23:20                 353
1.18-rc3.json                                      29-Nov-2021 05:03                 353
1.18.1.json                                        28-Feb-2022 15:04                 353
1.18.2.json                                        07-Jun-2022 16:08                 353
1.18.json                                          10-Dec-2021 13:16                 353
1.19.1.json                                        04-Aug-2022 10:41                 353
1.19.2.json                                        07-Dec-2022 16:12                 353
1.19.3.json                                        14-Mar-2023 16:36                 353
1.19.4.json                                        07-Jun-2023 15:58                 353
1.19.json                                          25-Jul-2022 09:01                 353
1.20.1.json                                        21-Sep-2023 16:40                 353
1.20.2.json                                        05-Dec-2023 16:43                 353
1.20.3.json                                        23-Apr-2024 15:25                 353
1.20.4.json                                        23-Apr-2024 15:25                 353
1.20.5.json                                        28-May-2024 21:03                 353
1.20.6.json                                        28-May-2024 21:03                 353
1.20.json                                          21-Sep-2023 16:40                 353
1.8.3.json                                         17-May-2015 09:44                 302
1.8.4.json                                         10-Dec-2021 01:54                 315
1.8.5.json                                         10-Dec-2021 01:54                 315
1.8.6.json                                         10-Dec-2021 01:54                 315
1.8.7.json                                         10-Dec-2021 01:54                 315
1.8.8.json                                         10-Dec-2021 01:54                 315
1.8.json                                           16-Apr-2015 22:00                 479
1.9.2.json                                         07-May-2016 06:41                 323
1.9.4.json                                         10-Dec-2021 01:54                 336
1.9.json                                           30-Mar-2016 16:03                 323
"""


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]


def _retrieve_versions() -> dict:
    versions = {}

    for line in txt.strip().splitlines():
        fields = line.split()
        json_file = fields[0]
        size = int(fields[-1])

        if '-' in json_file:  # -pre, -rc, ... -> Not interested!
            continue

        target = Path(__file__).parent / '.cache' / json_file
        if not target.exists() or target.stat().st_size != size:
            print(" > Working on:", json_file)
            target.parent.mkdir(exist_ok=True, parents=True)
            response = requests.get(version_url + json_file)
            target.write_bytes(response.content)
            data = response.json()
        else:
            data = json.loads(target.read_bytes())

        versions[target.stem] = data

    return versions


def _convert_java_class_version_to_java_version(nr1, nr2) -> tuple[int, int]:
    version_table = {
        49: 5,
        50: 6,
        51: 7,
        52: 8,
        53: 9,
        54: 10,
        55: 11,
        56: 12,
        57: 13,
        58: 14,
        59: 15,
        60: 16,
        61: 17,
        62: 18,
        63: 19,
        64: 20,
        65: 21,
        66: 22,
    }

    return version_table[nr1], version_table[nr2]


if __name__ == '__main__':
    versions = _retrieve_versions()
    for version in sorted(versions, key=natural_sort_key):
        data = versions[version]
        min_max = data.get('javaVersions', [51, 52])
        print(f'"{version}": {_convert_java_class_version_to_java_version(*min_max)},')
