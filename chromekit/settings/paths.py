"""Important path locations and setup."""
import os
from pathlib import Path


HOME = Path(os.path.expanduser('~'))
DOWNLOADS = HOME / 'Downloads'
LOCAL: Path = HOME / r'AppData/Local'
APPDATA: Path = LOCAL / 'ChromeKit'
DRIVER_EXECUTABLE = APPDATA / 'chromedriver_win32/chromedriver.exe'
LOGS = APPDATA / 'logs'
X86 = Path(r"C:/Program Files (x86)")
CHROME_EXECUTABLE = X86 / r'Google/Chrome/Application/chrome.exe'
CHROME_PROFILE = LOCAL / r'Google/Chrome/User Data/Default'


if not APPDATA.exists():
    APPDATA.mkdir()
if not LOGS.exists():
    LOGS.mkdir()
