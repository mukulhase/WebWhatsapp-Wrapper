from bs4 import BeautifulSoup
from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
import time
import os
driver = webdriver.Firefox()
url="web.whatsapp.com"
selectors = {
    'qrCode':"#window > div.entry-main > div.qrcode > img"
}
def init:
    driver.get(url)
    try:
        element = driver.find_element_by_css_selector(selectors['qrCode'])
    except:
        firstrun()

def firstrun():
    

def run():
    

init()
