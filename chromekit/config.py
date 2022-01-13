import logging
import pathlib
import os


PROJECT_NAME = 'ChromeKit'

# path setup
paths = dict()
paths['home'] = pathlib.Path(os.path.expanduser('~'))
paths['downloads'] = paths['home'] / 'Downloads'
paths['local'] = paths['home'] / r'AppData/Local'
paths['appdata'] = paths['local'] / 'ChromeKit'
paths['executable_path'] = (paths['appdata'] /
                            'chromedriver_win32/chromedriver.exe')
paths['logs'] = paths['appdata'] / 'logs'
paths['x86'] = pathlib.Path(r"C:/Program Files (x86)")
paths['chrome'] = paths['x86'] / r'Google/Chrome/Application/chrome.exe'
paths['profile'] = paths['local'] / r'Google/Chrome/User Data/Default'
paths['chromedriver'] = (paths['appdata'] /
                         r'chromedriver_win32/chromedriver.exe')

if not paths['appdata'].exists():
    paths['appdata'].mkdir()
if not paths['logs'].exists():
    paths['logs'].mkdir()

# debug settings
DEBUG = os.environ.get('CHROMEKITDEBUG') == 1

