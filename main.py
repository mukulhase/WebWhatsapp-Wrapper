import sys
sys.path.append('/home/lucas/Documentos/WhatsappTeste/WebWhatsapp-Wrapper')

import time, logging
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.message import Message

logging.getLogger().setLevel(logging.INFO)

driver = WhatsAPIDriver(client="chrome", executable_path="/home/lucas/chromedriver", loadstyles=True)
print("Waiting for QR")
driver.wait_for_login()

print("Bot started")

while True:
    time.sleep(3)
    print('Checking for more messages')
    for contact in driver.get_unread():
        for message in contact.messages:
            if isinstance(message, Message):  # Currently works for text messages only.
            	print(message.contact)
                #contact.chat.send_message(message.content)