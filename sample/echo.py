import time
from webwhatsapi import WhatsAPIDriver

driver = WhatsAPIDriver()
print("Waiting for QR")
driver.wait_for_login()

print("Bot started")

while True:
    time.sleep(3)
    print('Checking for more messages')
    for contact in driver.get_unread():
        for message in contact.messages:
            contact.chat.send_message(str(message))
