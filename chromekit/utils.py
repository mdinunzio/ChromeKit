import chromekit.config as cfg
import chromekit.logging
import requests
import zipfile
import subprocess
from bs4 import BeautifulSoup
import re
import os
import psutil
import ctypes
import sys


CHROMEDRIVER_URL = r'https://chromedriver.chromium.org'

log = chromekit.logging.get_logger(cfg.PROJECT_NAME)


def get_username():
    """Returns the OS username.

    """
    return os.path.expanduser('~').split(os.sep)[-1].lower()


def taskkill(image_name):
    """Kills a task with the given image name.

    """
    procs = [x for x in psutil.process_iter() if image_name in x.name()]
    for p in procs:
        p.kill()


def get_chrome_version():
    """Returns the version of Chrome on this PC.

    """
    cmd = r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" ' \
          r'/v version'
    res = subprocess.run(cmd, capture_output=True)
    version = res.stdout.decode('utf-8')
    version = version.split(' ')[-1]
    version = version.strip()
    return version


# def request_uac(task):
#     """Runs the given task after requesting UAC permissions.
#
#     """
#     params = str(cfg.paths.app + 'run.py') + f' --task {task}'
#     ctypes.windll.shell32.ShellExecuteW(
#         None, "runas", sys.executable, params, None, 1)


def get_chromedriver_version_map():
    """Returns a dictionary mapping Chrome versions to Chromedriver versions.

    """
    dl_url = f'{CHROMEDRIVER_URL}/downloads'
    req = requests.get(dl_url)
    soup = BeautifulSoup(req.text, 'html.parser')
    li_list = soup.find_all(
        lambda x:
        x.name == 'li'
        and 'If you are using Chrome version' in x.text)

    def extract_ver(x):
        return re.match(r'.* (?P<ver>\d*),.*', x.text).group('ver')

    def extract_href(x):
        return x.findChild('a').get('href')

    ver_map = {extract_ver(x): extract_href(x) for x in li_list}
    return ver_map


def download_chromedriver_zip(version=None, chunk_size=128):
    """Downloads the zip containing the specified Chromedriver version.

    Args:
        version (string): The version of Chromedriver to download.
            Defaults to None (automatically enforces compatibility with version
            of Chrome on system).
        chunk_size (int): The file chunk size for extraction. Defaults to 128.

    """
    log.info('Downloading Chromedriver zip file.')
    if version is None:
        version = get_chrome_version().split('.')[0]
    ver_map = get_chromedriver_version_map()
    if version not in ver_map:
        raise ValueError(f'Chromedriver for Chrome version {version} '
                         f'not available. Please update Chrome.')
    base_url = ver_map[version]
    cd_version = base_url.split('path=')[-1].strip().replace('/', '')
    dl_url = f'https://chromedriver.storage.googleapis.com/'
    dl_url += f'{cd_version}/chromedriver_win32.zip'
    zip_path = str(cfg.paths['downloads'] / f'chromedriver_win32.zip')
    req = requests.get(dl_url, stream=True)
    with open(zip_path, 'wb') as file:
        for chunk in req.iter_content(chunk_size=chunk_size):
            file.write(chunk)
    log.info('Finished downloading Chromedriver zip file.')
    return zip_path


def get_chromedriver_version(abridged=True):
    """Returns a string with the current chromedriver version.

    Args:
        abridged (bool): Whether or not to abridge the version string.
            Defaults to True.

    """
    if not cfg.paths['chromedriver'].exists():
        return
    cmd = str(cfg.paths['chromedriver']) + ' --version'
    res = subprocess.run(cmd, capture_output=True)
    version = res.stdout.decode('utf-8')
    if not abridged:
        return version
    version = version.split(' ')[1]
    version = version.strip()
    return version


def extract_chromedriver_zip(zip_path):
    """Extracts the chromedriver zip file to is appropriate location.

    By default, this is in the AppData/Local/ChromeKit folder.

    Args:
        zip_path (string): The path to the zip file containing the
            chromedriver executable.

    """
    log.info(f'Extracting chromedriver zip: {zip_path}')
    if not cfg.paths['chromedriver'].parent.exists():
        log.info(f'Creating chromedriver parent directory')
        cfg.paths['chromedriver'].parent.mkdir()
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(str(cfg.paths['chromedriver'].parent))
    log.info(f'Finished extracting chromedriver.')


def setup_chromedriver():
    """Sets up Chromedriver for this computer.

    """
    log.info('Setting up Chromedriver.')
    chrome_ver = get_chrome_version()
    log.info(f'Chrome version is {chrome_ver}')
    chrome_ver_short = chrome_ver.split('.')[0]
    zip_path = download_chromedriver_zip(chrome_ver_short)
    extract_chromedriver_zip(zip_path)
    log.info('Chromedriver setup complete.')


def ensure_driver_compatibility():
    """Downloads and sets up the a compatible driver version only if necessary.

    """
    driver_ver = get_chromedriver_version(abridged=True)
    if driver_ver is None:
        log.info('No Chromedriver detected. Beginning installation.')
        setup_chromedriver()
    chrome_ver = get_chrome_version()
    driver_split = [int(x) for x in driver_ver.split('.')]
    chrome_split = [int(x) for x in driver_ver.split('.')]
    ver_comps = min(len(driver_split), len(chrome_split))
    for i in range(ver_comps):
        if driver_split[i] < chrome_split[i]:
            log.info(f'Driver version {driver_ver} is less than '
                     f'Chrome version {chrome_ver}. '
                     f'Beginning Chromedriver re-installation.')
            setup_chromedriver()
        elif driver_split[i] > chrome_split[i]:
            log.info(f'Driver version {driver_ver} is greater than '
                     f'Chrome version {chrome_ver}. '
                     f'No need for driver update.')
            return
    log.info('Chrome version and driver version are equal.')
