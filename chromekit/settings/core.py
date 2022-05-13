"""Core package settings."""
import os


PACKAGE_NAME = 'ChromeKit'

IS_DEBUG = int(os.environ.get('CHROMEKITDEBUG', 0)) == 1
