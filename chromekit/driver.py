"""A simplified WebDriver module."""
import logging
import sys

import selenium.webdriver
import selenium.webdriver.chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException

import chromekit.settings
import chromekit.utils


logger = logging.getLogger(__name__)


class WebDriver(selenium.webdriver.Chrome):
    """A tool for interacting with webpages.

    Attributes:
        executable_path: The path to the Chromedriver exe.
        options: The webdriver Chrome options.
        profile: The path to the desired user's Chrome profile.

    """

    def __init__(self, use_default_profile: bool = False):
        """Inits the WebDriver.

        Args:
            use_default_profile: If true, the default user profile will
                be loaded, allowing for use of stored cookies etc.

        """
        self.executable_path: str = str(
            chromekit.settings.paths.DRIVER_EXECUTABLE)
        self.options: selenium.webdriver.chrome = (
            selenium.webdriver.ChromeOptions())
        self.profile: str = str(
            chromekit.settings.paths.CHROME_PROFILE)
        self.use_default_profile: bool = use_default_profile

        chromekit.utils.download_and_install_chromedriver_if_needed()

    def start(self):
        """Starts the chromedriver."""
        if self.use_default_profile:
            self.options.add_argument(f"user-data-dir={self.profile}")
        super().__init__(executable_path=self.executable_path,
                         options=self.options)

    def await_element(self, criteria: str, by_type: str = By.CSS_SELECTOR,
                      ec_type: type = ec.element_to_be_clickable,
                      timeout: int = 60, fatal: bool = False
                      ) -> selenium.webdriver.remote.webelement.WebElement:
        """Returns an element on a page after it has finished rendering.

        Args:
            criteria: The criteria defining the scope of the search.
            by_type: The type of match to
                be performed. Defaults to By.CSS_SELECTOR.
                For a full list of by_types see
                selenium-python.readthedocs.io/api.html#locate-elements-by
            ec_type: The condition that must be met for an element to be
                considered found. Defaults to ec.element_to_be_clickable.
                For a full list of conditions see
                selenium-python.readthedocs.io/waits.html.
            timeout: The number of seconds after which to time out.
            fatal: If True, the driver will be killed if the element is
                not found. Defaults to False.
        """
        try:
            wdw = WebDriverWait(self, timeout)
            exp_cond = ec_type((by_type, criteria))
            element = wdw.until(exp_cond)
            return element
        except TimeoutException as timeout_exception:
            logger.info('TimeoutException: Element not found.')
            if fatal:
                raise timeout_exception
            return None

    def jsclick(self, element: selenium.webdriver.remote.webelement.WebElement,
                fatal: bool = True):
        """Clicks an element using javascript

        This helps avoid the ElementClickInterceptedException.

        Args:
            element: The element to be clicked.
            fatal: If True, the driver will be killed should an
                exception be thrown. Defaults to True.

        """
        try:
            javascript = 'arguments[0].click();'
            self.execute_script(javascript, element)
        except Exception as exception:
            logger.exception(exception)
            if fatal:
                self.quit()
                sys.exit(1)
