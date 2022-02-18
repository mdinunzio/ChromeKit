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

log = logging.getLogger(__name__)


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
    """Returns the version of Chrome on this PC.

    """
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
    """Returns a dictionary mapping Chrome versions to Chromedriver versions.

    """
    dl_url = f'{CHROMEDRIVER_URL}/downloads'
    req = requests.get(dl_url)
    soup = BeautifulSoup(req.text, 'html.parser')
    li_list = soup.find_all(
        lambda x:
        x.name == 'list_item'
        and 'If you are using Chrome version' in x.text)

    def extract_ver(list_item):
        return re.match(r'.* (?P<ver>\d*),.*', list_item.text).group('ver')

    def extract_href(list_item):
        return list_item.findChild('a').get('href')

    ver_map = {extract_ver(x): extract_href(x) for x in li_list}
    return ver_map


def download_chromedriver_zip(version: str = None, chunk_size: int = 128
                              ) -> str:
    """Downloads the zip containing the specified Chromedriver version.

    Args:
        version: The version of Chromedriver to download.
            Defaults to None (automatically enforces compatibility with version
            of Chrome on system).
        chunk_size: The file chunk size for extraction. Defaults to 128.

    """
    log.debug('Downloading Chromedriver zip file.')
    if version is None:
        version = get_chrome_version().split('.')[0]
    ver_map = fetch_chrome_to_chromedriver_version_map()
    if version not in ver_map:
        raise ValueError(f'Chromedriver for Chrome version {version} '
                         f'not available. Please update Chrome.')
    base_url = ver_map[version]
    cd_version = base_url.split('path=')[-1].strip().replace('/', '')
    dl_url = f'https://chromedriver.storage.googleapis.com/'
    dl_url += f'{cd_version}/chromedriver_win32.zip'
    zip_path = str(chromekit.settings.PATHS.downloads /
                   f'chromedriver_win32.zip')
    req = requests.get(dl_url, stream=True)
    with open(zip_path, 'wb') as file:
        for chunk in req.iter_content(chunk_size=chunk_size):
            file.write(chunk)
    log.debug('Finished downloading Chromedriver zip file.')
    return zip_path


def extract_chromedriver_zip_to_appdata(zip_path: str):
    """Extracts the chromedriver zip file to is appropriate location.

    By default, this is in the AppData/Local/ChromeKit folder.

    Args:
        zip_path (string): The path to the zip file containing the
            chromedriver executable.

    """
    log.debug('Extracting chromedriver zip: %s', zip_path)
    if not chromekit.settings.PATHS.chromedriver.parent.exists():
        log.debug('Creating chromedriver parent directory')
        chromekit.settings.PATHS.chromedriver.parent.mkdir()
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(
            str(chromekit.settings.PATHS.chromedriver.parent))
    log.debug('Finished extracting chromedriver.')


def get_chromedriver_version(abridged: bool = True) -> Optional[str]:
    """Returns the current chromedriver version.

    Args:
        abridged: Whether or not to abridge the version string.
            Defaults to True.

    """
    if not chromekit.settings.PATHS.chromedriver.exists():
        return
    cmd = str(chromekit.settings.PATHS.chromedriver) + ' --version'
    res = subprocess.run(cmd, capture_output=True, check=True)
    version = res.stdout.decode('utf-8')
    if not abridged:
        return version
    version = version.split(' ')[1]
    version = version.strip()
    return version


def install_chromedriver():
    """Installs Chromedriver in the appropriate directory from the web.

    """
    log.info('Setting up Chromedriver.')
    chrome_ver = get_chrome_version()
    log.info('Chrome version is %s', chrome_ver)
    chrome_ver_short = chrome_ver.split('.')[0]
    zip_path = download_chromedriver_zip(chrome_ver_short)
    extract_chromedriver_zip_to_appdata(zip_path)
    log.info('Chromedriver setup complete.')


def update_driver(force: bool = False):
    """Downloads installs a compatible driver version if necessary.

    Args:
        force: If True, the driver will be reinstalled even if the
            Chrome and Chromedriver versions are already compatible.

    """
    if force:
        log.info('Force-installing Chromedriver')
        install_chromedriver()
    driver_ver = get_chromedriver_version(abridged=True)
    if driver_ver is None:
        log.info('No Chromedriver detected. Beginning installation.')
        install_chromedriver()
    chrome_ver = get_chrome_version()
    driver_ver_tuple = tuple(int(x) for x in driver_ver.split('.'))
    chrome_ver_tuple = tuple(int(x) for x in chrome_ver.split('.'))
    if driver_ver_tuple < chrome_ver_tuple:
        log.info(
            'Driver version %s is less than '
            'Chrome version %s. '
            'Beginning Chromedriver re-installation.',
            driver_ver, chrome_ver)
        install_chromedriver()
    elif driver_ver_tuple > chrome_ver_tuple:
        log.debug(
            'Driver version %s is greater than '
            'Chrome version %s. '
            'No need for driver update.',
            driver_ver, chrome_ver)
        return
    log.debug('Chrome version and driver version are equal. '
              'No need to update.')
