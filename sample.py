import time
from webwhatsapp import WhatsAPIDriver
print "waiting for QR"
driver = WhatsAPIDriver()
driver.first_run()
time.sleep(10)
driver.get_unread()
print "bot started"
while True:
	time.sleep(10)
	print('checking for more messages')
	for contact in driver.get_unread():
		for message in contact[u'messages']:
			driver.send_to_whatsapp_id(contact[u'id'],message[u'message'])
