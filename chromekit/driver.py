"""A simplified webdriver module.

"""
import chromekit.config as cfg
import chromekit.logging
import chromekit.utils
import selenium.webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
import sys


log = chromekit.logging.get_logger(cfg.PROJECT_NAME)


class WebDriver(selenium.webdriver.Chrome):
    def __init__(self):
        """A tool for interacting with webpages.

        """
        self.executable_path = cfg.paths['executable_path']
        self.options = selenium.webdriver.ChromeOptions()
        self.profile = cfg.paths['profile']
        self.options.add_argument(f"user-data-dir={self.profile}")
        chromekit.utils.ensure_driver_compatibility()

    def start(self):
        """Starts the chromedriver"""
        super().__init__(executable_path=self.executable_path,
                         options=self.options)
        self.maximize_window()

    def await_element(self, criteria, by_type=By.CSS_SELECTOR,
                      ec_type=ec.element_to_be_clickable, timeout=300,
                      fatal=True):
        """Returns an element on a page after it has finished rendering.

        """
        try:
            wdw = WebDriverWait(self.driver, timeout)
            exp_cond = ec_type((by_type, criteria))
            element = wdw.until(exp_cond)
            return element
        except TimeoutException:
            print('TimeoutException: Element not found.')
            if fatal:
                self.driver.quit()
                sys.exit(1)

    def find_element(self, criteria):
        """Returns an element if it exists, otherwise return None.

        """
        elements = self.driver.find_elements(By.CSS_SELECTOR, criteria)
        if len(elements) > 0:
            return elements[0]
        else:
            return None

    def jsclick(self, element, fatal=True):
        """Clicks an element using javascript

        This helps avoid the ElementClickInterceptedException.

        """
        try:
            js = 'arguments[0].click();'
            self.execute_script(js, element)
        except Exception as e:
            print(e)
            if fatal:
                self.quit()
                sys.exit(1)
