import pathlib
import os


PROJECT_NAME = 'ChromeKit'

# Define key paths.
PATHS = dict()
PATHS['home'] = pathlib.Path(os.path.expanduser('~'))
PATHS['downloads'] = PATHS['home'] / 'Downloads'
PATHS['local'] = PATHS['home'] / r'AppData/Local'
PATHS['appdata'] = PATHS['local'] / 'ChromeKit'
PATHS['executable_path'] = (
        PATHS['appdata'] / 'chromedriver_win32/chromedriver.exe')
PATHS['logs'] = PATHS['appdata'] / 'logs'
PATHS['x86'] = pathlib.Path(r"C:/Program Files (x86)")
PATHS['chrome'] = PATHS['x86'] / r'Google/Chrome/Application/chrome.exe'
PATHS['profile'] = PATHS['local'] / r'Google/Chrome/User Data/Default'
PATHS['chromedriver'] = (
        PATHS['appdata'] / r'chromedriver_win32/chromedriver.exe')

if not PATHS['appdata'].exists():
    PATHS['appdata'].mkdir()
if not PATHS['logs'].exists():
    PATHS['logs'].mkdir()

# debug settings
DEBUG = os.environ.get('CHROMEKITDEBUG') == 1
