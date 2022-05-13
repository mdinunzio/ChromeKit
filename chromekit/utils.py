"""Utilities for utilizing the WebDriver.

"""
import ctypes
import logging
import os
import re
import subprocess
import sys
from typing import Optional
import zipfile

from bs4 import BeautifulSoup
import psutil
import requests

import chromekit.settings


CHROMEDRIVER_URL = r'https://chromedriver.chromium.org'

logger = logging.getLogger(__name__)


def get_username() -> str:
    """Returns the OS username.

    """
    return os.path.expanduser('~').split(os.sep)[-1].lower()


def taskkill(image_name: str):
    """Kills a task with the given image name."""
    processes = [x for x in psutil.process_iter() if image_name in x.name()]
    for process in processes:
        process.kill()


def get_chrome_version() -> str:
    """Returns the version of Chrome on this PC."""
    cmd = r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" ' \
          r'/v version'
    res = subprocess.run(cmd, capture_output=True, check=True)
    version = res.stdout.decode('utf-8')
    version = version.split(' ')[-1]
    version = version.strip()
    return version


def request_uac(command: str):
    """Runs the given task after requesting UAC permissions."""
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, command, None, 1)


def fetch_chrome_to_chromedriver_version_map() -> dict:
    """Returns a dictionary mapping Chrome versions to Chromedriver versions."""
    dowload_url = f'{CHROMEDRIVER_URL}/downloads'
    req = requests.get(dowload_url)
    soup = BeautifulSoup(req.text, 'html.parser')
    li_list = soup.find_all('li')
    li_list = [x for x in li_list if x.text is not None]
    li_list = [x for x in li_list if 'you are using Chrome version' in x.text]

    def extract_ver(list_item):
        return re.match(r'.* (?P<ver>\d*),.*', list_item.text).group('ver')

    def extract_href(list_item):
        return list_item.findChild('a').get('href')

    ver_map = {extract_ver(x): extract_href(x) for x in li_list}
    return ver_map


def download_chromedriver_zip(chrome_version: str = None, chunk_size: int = 128
                              ) -> str:
    """Downloads the zip containing the specified Chromedriver version.

    Args:
        chrome_version: The version of Chrome for which to download a
            compatible Chromedriver executable. Defaults to the version
            of Chrome on this PC.
        chunk_size: The file chunk size for extraction. Defaults to 128.

    """
    logger.info('Downloading Chromedriver zip file.')
    if chrome_version is None:
        chrome_version = get_chrome_version()
    major_version = chrome_version.split('.')[0]
    version_map = fetch_chrome_to_chromedriver_version_map()
    if major_version not in version_map:
        raise ValueError(f'Chromedriver for Chrome version {chrome_version} '
                         f'not available. Please update Chrome.')
    base_url = version_map[major_version]
    cd_version = base_url.split('path=')[-1].strip().replace('/', '')
    download_url = 'https://chromedriver.storage.googleapis.com/'
    download_url += f'{cd_version}/chromedriver_win32.zip'
    zip_path = str(chromekit.settings.paths.DOWNLOADS /
                   'chromedriver_win32.zip')
    req = requests.get(download_url, stream=True)
    with open(zip_path, 'wb') as file:
        for chunk in req.iter_content(chunk_size=chunk_size):
            file.write(chunk)
    logger.info('Finished downloading Chromedriver zip file.')
    return zip_path


def extract_chromedriver_zip(zip_path: str):
    """Extracts the chromedriver zip file to is appropriate location.

    Args:
        zip_path (string): The path to the zip file containing the
            chromedriver executable.

    """
    unzip_path = chromekit.settings.paths.DRIVER_EXECUTABLE.parent
    logger.info('Extracting chromedriver from %s to %s',
                zip_path, unzip_path)
    if not unzip_path.exists():
        logger.info('Creating chromedriver parent directory (%s)', unzip_path)
        unzip_path.mkdir()
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(str(unzip_path))
    logger.info('Finished extracting chromedriver.')


def get_chromedriver_version() -> Optional[str]:
    """Returns the current chromedriver version."""
    logger.debug('Getting chromedriver version.')
    if not chromekit.settings.paths.DRIVER_EXECUTABLE.exists():
        logger.debug('No chromedriver executable exists.')
        return None
    cmd = str(chromekit.settings.paths.DRIVER_EXECUTABLE) + ' --version'
    cmd_result = subprocess.run(cmd, capture_output=True, check=True)
    version = cmd_result.stdout.decode('utf-8')
    version = version.split(' ')[1]
    version = version.strip()
    logger.debug('Chromedriver version is: %s', version)
    return version


def download_and_install_chromedriver():
    """Installs Chromedriver in the appropriate directory from the web."""
    logger.info('Downloading and installing up Chromedriver.')
    chrome_version = get_chrome_version()
    logger.info('Chrome version is %s', chrome_version)
    zip_path = download_chromedriver_zip(chrome_version)
    extract_chromedriver_zip(zip_path)
    logger.info('Chromedriver setup complete.')


def download_and_install_chromedriver_if_needed(force: bool = False):
    """Downloads and installs a compatible driver version if necessary.

    Args:
        force: If True, the driver will be reinstalled even if the
            Chrome and Chromedriver versions are already compatible.
    """
    if force:
        logger.info('Force-installing Chromedriver.')
        download_and_install_chromedriver()
    driver_version = get_chromedriver_version()
    if driver_version is None:
        logger.info('No Chromedriver detected. Beginning installation.')
        download_and_install_chromedriver()
    chrome_version = get_chrome_version()
    driver_ver_tuple = tuple(int(x) for x in driver_version.split('.'))
    chrome_ver_tuple = tuple(int(x) for x in chrome_version.split('.'))
    if driver_ver_tuple < chrome_ver_tuple:
        logger.info('Driver version %s is less than '
                    'Chrome version %s. '
                    'Beginning Chromedriver re-installation.',
                    driver_version, chrome_version)
        download_and_install_chromedriver()
    elif driver_ver_tuple > chrome_ver_tuple:
        logger.info('Driver version %s is greater than '
                    'Chrome version %s. '
                    'No need for driver update.',
                    driver_version, chrome_version)
    else:
        logger.info('Chrome version and driver version are equal. '
                    'No need to update.')
