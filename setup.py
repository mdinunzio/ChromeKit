from setuptools import setup


setup(
    name="chromekit",
    version="2.0.9",
    author="Michael DiNunzio",
    author_email="mdinunzio@gmail.com",
    packages=['chromekit', 'chromekit.settings'],
    description="A utility for easily maintaining and accessing ChromeDriver.",
    keywords="ChromeDriver Selenium WebDriver",
    url="https://github.com/mdinunzio/ChromeKit",
    install_requires=[
        "beautifulsoup4",
        "psutil",
        "selenium",
        "webdriver_manager"]
)
