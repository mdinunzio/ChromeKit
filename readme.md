#ChromeKit
A utility for simplifying the use of Selenium with Chrome.

This package automatically checks and updates ChromeDriver to 
match your particular version of Chrome.

Additionally, it adds a handful of useful commands to Selenium's API.

## Installation
```
pip install git+https://github.com/mdinunzio/ChromeKit.git
```

## Examples
```
import chromekit.driver


driver = chromekit.driver.WebDriver()
driver.start()
driver.get('http://www.google.com')
```