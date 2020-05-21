import os, sys
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

print "Environment", os.environ
try:
    os.environ["SELENIUM"]
except KeyError:
    print "Please set the environment variable SELENIUM to Selenium URL"
    sys.exit(1)

driver = webdriver.Remote(
    command_executor=os.environ["SELENIUM"],
    desired_capabilities=DesiredCapabilities.FIREFOX,
)

print "Driver initialized"
print "Getting https://web.whatsapp.com"
driver.get("https://web.whatsapp.com")
driver.save_screenshot("shot.png")
print "Screenshot saved"
driver.close()
print "Driver closed"
