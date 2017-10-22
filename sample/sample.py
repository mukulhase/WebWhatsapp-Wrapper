import time
from webwhatsapi import WhatsAPIDriver
print "waiting for QR"
driver = WhatsAPIDriver()
driver.firstrun()
driver.view_unread()
print "bot started"
while True:
	time.sleep(1)
	print('checking for more messages')
	for contact in driver.view_unread():
		for message in contact[u'messages']:
			driver.send_to_whatsapp_id(contact[u'id'],message[u'message'])
