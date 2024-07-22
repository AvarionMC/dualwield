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
    "1.8": (7, 8),
    "1.8.3": (7, 8),
    "1.8.4": (7, 8),
    "1.8.5": (7, 8),
    "1.8.6": (7, 8),
    "1.8.7": (7, 8),
    "1.8.8": (7, 8),
    "1.9": (7, 8),
    "1.9.2": (7, 8),
    "1.9.4": (7, 8),
    "1.10": (7, 8),
    "1.10.2": (7, 8),
    "1.11": (7, 8),
    "1.11.1": (7, 8),
    "1.11.2": (7, 8),
    "1.12": (8, 8),
    "1.12.1": (8, 9),
    "1.12.2": (8, 10),
    "1.13": (8, 11),
    "1.13.1": (8, 11),
    "1.13.2": (8, 12),
    "1.14": (8, 12),
    "1.14.1": (8, 12),
    "1.14.2": (8, 12),
    "1.14.3": (8, 12),
    "1.14.4": (8, 13),
    "1.15": (8, 13),
    "1.15.1": (8, 13),
    "1.15.2": (8, 14),
    "1.16.1": (8, 14),
    "1.16.2": (8, 14),
    "1.16.3": (8, 15),
    "1.16.4": (8, 15),
    "1.16.5": (8, 16),
    "1.17": (16, 16),
    "1.17.1": (16, 17),
    "1.18": (17, 17),
    "1.18.1": (17, 17),
    "1.18.2": (17, 18),
    "1.19": (17, 18),
    "1.19.1": (17, 18),
    "1.19.2": (17, 19),
    "1.19.3": (17, 20),
    "1.19.4": (17, 20),
    "1.20": (17, 21),
    "1.20.1": (17, 21),
    "1.20.2": (17, 21),
    "1.20.4": (17, 22),
    "1.20.6": (21, 22),
}
__dir__ = Path(__file__).parent.resolve().absolute()
__root__ = __dir__.parent.parent
m2_buildtools = Path.home().joinpath('.m2/BuildTools.jar').resolve().absolute()


def find_version_to_build(directory: Path) -> tuple[str, str]:
    pom = directory.joinpath('pom.xml').read_text()
    return re.search(r'<spigot.version>\s*((.*)-R0.1-SNAPSHOT)\s*</spigot.version>', pom).groups()


def get_java_path(version: str) -> str:
    versions = version.split('.')
    min_java, max_java = -1, -1

    for version_needed in [version, ".".join(versions[:3]), ".".join(versions[:2]), versions[1]]:
        if version_needed not in java_versions_needed:
            continue

        min_java, max_java = java_versions_needed[version_needed]

        for java_version in range(min_java, max_java + 1):
            java_path = os.getenv(f'JAVA_HOME_{java_version}_X64')
            if java_path:
                return java_path + '/bin/java'

            alternative = Path(f"/usr/lib/jvm/java-{java_version}-openjdk-amd64/bin/java")
            if alternative.exists():
                return str(alternative)

        break  # First one should stop the loop for searching!

    raise Exception(f"No JAVA_HOME found for version {version}, I need something between '{min_java}' and '{max_java}'")


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

    with open(__dir__ / f"log.{version}.txt", "w") as file:
        logger.info(f" > .. building")
        subprocess.run(command, stdout=file, stderr=subprocess.STDOUT, check=True)
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
