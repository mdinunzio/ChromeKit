"""A Chrome WebDriver module with useful feature add-ons."""
import logging
from typing import Callable, Optional

import selenium.webdriver
import selenium.webdriver.chrome
import selenium.webdriver.chrome.service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote import webelement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
import webdriver_manager.chrome

import chromekit.settings
import chromekit.utils


logger = logging.getLogger(__name__)


class WebDriver(selenium.webdriver.Chrome):
    """A tool for interacting with webpages.

    Attributes:
        options: The options for Chrome used by the driver.
        profile_path: The path to the desired user's Chrome profile.

    """

    def __init__(self, use_default_profile: bool = False):
        """Initializes the WebDriver.

        Args:
            use_default_profile: If true, the default user profile_path will
                be loaded, allowing for use of stored cookies etc.

        """
        self.options: selenium.webdriver.chrome = (
            selenium.webdriver.ChromeOptions())
        self.profile_path: str = str(
            chromekit.settings.paths.CHROME_PROFILE)
        self.use_default_profile: bool = use_default_profile

    def start(self):
        """Starts the Chrome WebDriver."""
        if self.use_default_profile:
            self.options.add_argument(f"user-data-dir={self.profile_path}")

        chrome_driver_manager = webdriver_manager.chrome.ChromeDriverManager()
        service = selenium.webdriver.chrome.service.Service(
            chrome_driver_manager.install())

        super().__init__(service=service, options=self.options)

    def await_element(self, criteria: str, by_type: str = By.CSS_SELECTOR,
                      ec_type: Callable = ec.element_to_be_clickable,
                      timeout: int = 60, fatal: bool = False
                      ) -> Optional[webelement.WebElement]:
        """Returns an element on a page after it has finished rendering.

        Args:
            criteria: The criteria defining the scope of the search.
            by_type: The type of match to be performed.
                Defaults to By.CSS_SELECTOR. For a full list of by_types see
                selenium-python.readthedocs.io/api.html#locate-elements-by
            ec_type: The condition that must be met for an element to be
                considered found. Defaults to ec.element_to_be_clickable.
                For a full list of conditions see
                selenium-python.readthedocs.io/waits.html.
            timeout: The number of seconds after which to time out.
                Defaults to 60
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
                self.quit()
                raise timeout_exception
            return None

    def js_click(self, element: webelement.WebElement):
        """Clicks an element using javascript.

        This helps avoid the ElementClickInterceptedException.

        Args:
            element: The element to be clicked.

        """
        javascript = 'arguments[0].click();'
        self.execute_script(javascript, element)
