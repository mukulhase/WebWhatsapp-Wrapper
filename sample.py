import time
from webwhatsapp import WhatsAPIDriver
print "waiting for QR"
driver = WhatsAPIDriver()
driver.firstrun()
print "bot started"
driver.view_unread()
while True:
	time.sleep(1)
	contacts = driver.view_unread()
	print(contacts)
	for contact in contacts:
		##filters here
		##if "Mom" in contact[u"contact"]:
		if True:
			for message in contact[u"messages"]:
				##message here
				print message
				##driver.send_to_whatsapp_id(contact[u"id"], "echo" + message[u"message"])