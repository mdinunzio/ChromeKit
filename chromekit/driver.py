"""A simplified webdriver module.

"""
import chromekit.config as cfg
import chromekit.utils
import selenium.webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
import logging
import sys


log = logging.getLogger(__name__)


class WebDriver(selenium.webdriver.Chrome):
    """A tool for interacting with webpages.

    Attributes:
        executable_path (string): The path to the Chromedriver exe.
        options (ChromeOptions): The webdriver Chrome options.
        profile (string): The path to the desired user's Chrome profile.

    """

    def __init__(self, use_default_profile=False):
        """Inits the WebDriver.

        Args:
            use_default_profile (bool): If true, the default user profile will
                be loaded, allowing for use of stored cookies etc.

        """
        self.executable_path = str(cfg.PATHS['executable_path'])
        self.options = selenium.webdriver.ChromeOptions()
        self.profile = str(cfg.PATHS['profile'])
        self.use_default_profile = use_default_profile
        chromekit.utils.ensure_driver_compatibility()

    def start(self):
        """Starts the chromedriver.

        """
        if self.use_default_profile:
            self.options.add_argument(f"user-data-dir={self.profile}")
        super().__init__(executable_path=self.executable_path,
                         options=self.options)
        self.maximize_window()

    def await_element(self, criteria, by_type=By.CSS_SELECTOR,
                      ec_type=ec.element_to_be_clickable, timeout=60,
                      fatal=False):
        """Returns an element on a page after it has finished rendering.

        Args:
            criteria (str): The criteria defining the scope of the search.
            by_type (selenium.webdriver.common.by.By): The type of match to
                be performed. Defaults to By.CSS_SELECTOR.
                For a full list of by_types see
                selenium-python.readthedocs.io/api.html#locate-elements-by
            ec_type (selenium.webdriver.support.expected_conditions): The
                condition that must be met for an element to be considered
                found. Defaults to ec.element_to_be_clickable.
                For a full list of conditions see
                selenium-python.readthedocs.io/waits.html.
            timeout (int): The number of seconds after which to time out.
            fatal (bool): If True, the driver will be killed if the element is
                not found. Defaults to False.

        """
        try:
            wdw = WebDriverWait(self, timeout)
            exp_cond = ec_type((by_type, criteria))
            element = wdw.until(exp_cond)
            return element
        except TimeoutException:
            print('TimeoutException: Element not found.')
            if fatal:
                self.quit()
                sys.exit(1)

    def jsclick(self, element, fatal=True):
        """Clicks an element using javascript

        This helps avoid the ElementClickInterceptedException.

        Args:
            element (selenium.webdriver.remote.webelement.WebElement): The
                element to be clicked.
            fatal (bool): If True, the driver will be killed should an
                exception be thrown. Defaults to True.

        """
        try:
            js = 'arguments[0].click();'
            self.execute_script(js, element)
        except Exception as e:
            print(e)
            if fatal:
                self.quit()
                sys.exit(1)
