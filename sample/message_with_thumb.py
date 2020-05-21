import os
import sys

from webwhatsapi import WhatsAPIDriver

try:
    os.environ["SELENIUM"]
except KeyError:
    print("Please set the environment variable SELENIUM to Selenium URL")
    sys.exit(1)

try:
    os.environ["MY_PHONE"]
except KeyError:
    print("Please set the environment variable SELENIUM to Selenium URL")
    sys.exit(1)

profiledir = os.path.join(".", "firefox_cache")
if not os.path.exists(profiledir):
    os.makedirs(profiledir)
driver = WhatsAPIDriver(
    profile=profiledir, client="remote", command_executor=os.environ["SELENIUM"]
)

print("Waiting for QR")
driver.wait_for_login()
print("Saving session")
driver.save_firefox_profile(remove_old=False)
print("Bot started")

logo = "./docs/logo/logomark-01.png"

chat = driver.get_chat_from_phone_number(os.environ["MY_PHONE"])

chat.send_message_with_thumb(
    logo,
    "https://github.com/mukulhase/WebWhatsapp-Wrapper",
    "Whatsapp Wrapper!",
    "(Based on web.whatsapp.com)",
    """
    This package is used to provide a python interface for interacting with WhatsAPP Web to send and
     receive Whatsapp messages. It is based on the official Whatsapp Web Browser
      Application and uses Selenium browser automation to communicate with Whatsapp Web.
    https://github.com/mukulhase/WebWhatsapp-Wrapper
    """,
)
