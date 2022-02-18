from dataclasses import dataclass
from pathlib import Path
import os


PROJECT_NAME = 'ChromeKit'


# Define key paths.
@dataclass
class _Paths:
    home: Path = Path(os.path.expanduser('~'))
    downloads: Path = home / 'Downloads'
    local: Path = home / r'AppData/Local'
    appdata: Path = local / 'ChromeKit'
    executable_path: Path = appdata / 'chromedriver_win32/chromedriver.exe'
    logs: Path = appdata / 'logs'
    x86: Path = Path(r"C:/Program Files (x86)")
    chrome: Path = x86 / r'Google/Chrome/Application/chrome.exe'
    profile: Path = local / r'Google/Chrome/User Data/Default'
    chromedriver: Path = appdata / r'chromedriver_win32/chromedriver.exe'


PATHS = _Paths()

if not PATHS.appdata.exists():
    PATHS.appdata.mkdir()
if not PATHS.logs.exists():
    PATHS.logs.mkdir()

# debug settings
DEBUG = os.environ.get('CHROMEKITDEBUG') == 1
