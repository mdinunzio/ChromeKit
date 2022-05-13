"""Utilities to accompany the main WebDriver functionality."""
import ctypes
import logging
import os
import subprocess
import sys

import psutil


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
    cmd = (r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" '
           r'/v version')
    res = subprocess.run(cmd, capture_output=True, check=True)
    version = res.stdout.decode('utf-8')
    version = version.split(' ')[-1]
    version = version.strip()
    return version


def request_uac(command: str):
    """Runs the given task after requesting UAC permissions."""
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, command, None, 1)
