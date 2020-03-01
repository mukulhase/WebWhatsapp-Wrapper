import os
import sys
import time
import json
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.message import Message, MediaMessage

try:
    os.environ["SELENIUM"]
except KeyError:
    print("Please set the environment variable SELENIUM to Selenium URL")
    sys.exit(1)

# Save session on "/firefox_cache/localStorage.json".
# Create the directory "/firefox_cache", it's on .gitignore
# The "app" directory is internal to docker, it corresponds to the root of the project.
# The profile parameter requires a directory not a file.

profiledir = os.path.join(".", "firefox_cache")
if not os.path.exists(profiledir):
    os.makedirs(profiledir)
driver = WhatsAPIDriver(profile=profiledir, client='remote', command_executor=os.environ["SELENIUM"])
print("Waiting for QR")
driver.wait_for_login()
print("Saving session")
driver.save_firefox_profile(remove_old=False)
print("Bot started")

chat = driver.get_chat_from_phone_number('YOUR_PHONE')


chat.send_message_with_thumb(
    'IMAGE_PATH.[png|jpg]',
    'https://www.ic.unicamp.br/~stolfi/misc/misc/FlatEarth/FlatEarthAndBible.html',
    'FLAT EARTH TITLE',
    'When I first became interested in the flat-earthers in the early 1970s...',
    """
    When I first became interested in the flat-earthers in the early 1970s, 
    I was surprised to learn that flat-earthism in the English-speaking world is and 
    always has been entirely based upon the Bible. 
    https://www.ic.unicamp.br/~stolfi/misc/misc/FlatEarth/FlatEarthAndBible.html
    """
)
