#!env python
"""
You'll need these versions to compile the server jars:
# Java 8: 1.9 -> 1.16
# Java 16: 1.17
# Java 17: 1.18+
"""
import logging
import os
import re
import subprocess
from functools import lru_cache
from pathlib import Path

import requests

logging.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

java_versions_needed = {
    '9': 8,
    '10': 8,
    '11': 8,
    '12': 8,
    '13': 8,
    '14': 8,
    '15': 8,
    '16': 8,
    '17': 16,
    '18': 17,
    '19': 17,
    '20': 17,
}
__dir__ = Path(__file__).parent.resolve().absolute()
__root__ = __dir__.parent.parent
m2_buildtools = Path.home().joinpath('.m2/BuildTools.jar').resolve().absolute()


def find_version_to_build(directory: Path) -> tuple[str, str]:
    pom = directory.joinpath('pom.xml').read_text()
    return re.search(r'<spigot.version>\s*((.*)-R0.1-SNAPSHOT)\s*</spigot.version>', pom).groups()


def get_java_path(version: str) -> str:
    minor = version.split('.')[1]
    java_version = java_versions_needed[minor]

    java_path = os.getenv(f'JAVA_HOME_{java_version}_X64')
    if not java_path:
        raise Exception(f"No JAVA_HOME found for version {version}")

    return java_path + '/bin/java'


def run_build_tools(version: str, spigot_needed: str) -> None:
    m2_location = Path.home() / f'.m2/repository/org/spigotmc/spigot/{spigot_needed}/spigot-{spigot_needed}.jar'
    if m2_location.exists():
        logger.info(" > Already built.")
        return

    command = [
        get_java_path(version=version),
        "-jar",
        m2_buildtools,
        "--remapped",
        "--rev",
        version
    ]

    log = __dir__ / f"log.{version}.txt"
    with open(log, "w") as file:
        logger.info(f" > .. building")
        result = subprocess.run(command, stdout=file, stderr=subprocess.STDOUT)
    if result.returncode:
        print(log.read_text()[-5000:])
        raise SystemExit(f"BuildTools failed for {version}")
    logger.info(f" > .. finished")


def prepare_build_tools():
    logging.info("Checking if BuildTools.jar exists:")
    if m2_buildtools.exists():
        logging.info(" .. OK!")
        return

    logging.info(" .. downloading")
    response = requests.get('https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar')
    m2_buildtools.write_bytes(response.content)
    logging.info(" .. done")

    return m2_buildtools


if __name__ == '__main__':
    prepare_build_tools()

    for directory in __root__.glob('v1_*'):
        logger.info("Found directory '%s'", directory.name)
        spigot_needed, full_version = find_version_to_build(directory)

        logger.info(f" > Corresponding spigot version: %s", full_version)
        run_build_tools(version=full_version, spigot_needed=spigot_needed)
