import os, sys
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


driver = webdriver.Remote(
        command_executor="http://127.0.0.1:4444/wd/hub",
        desired_capabilities=DesiredCapabilities.FIREFOX
    )

print("Driver initialized")
print("Getting https://web.whatsapp.com")
driver.get("https://web.whatsapp.com")
driver.save_screenshot('shot.png')
print("Screenshot saved")
driver.close()
print("Driver closed")
