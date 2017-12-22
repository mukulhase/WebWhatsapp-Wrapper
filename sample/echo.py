# Not recent. Will be updated after changes

import time
from webwhatsapi import WhatsAPIDriver

driver = WhatsAPIDriver()
print "Waiting for QR"
driver.wait_for_login()

print "Bot started"

while True:
	time.sleep(3)
	print('Checking for more messages')
	for contact in driver.view_unread():
		for message in contact[u'messages']:
			driver.send_to_whatsapp_id(contact[u'id'], message[u'message'])
