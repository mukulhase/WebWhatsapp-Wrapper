import time
from webwhatsapp import WhatsAPIDriver
driver = WhatsAPIDriver()
driver.firstrun()
print "bot started"
while True:
	time.sleep(1)
	contacts = driver.view_unread();
	for contact in contacts:
		##filters here
		##if "Mom" in contact[u"contact"]:
		if True:
			for message in contact[u"messages"]:
				##message here
				msg=message[u'message']
				#If audio print print message if not continue with messages
				if msg is None:
					print "This is audio"
				else:
					#Display message on the screen!
					print 'Escuchando --> ' + message[u'message']  
				
					driver.send_to_id(contact[u"id"], contact[u"contact"], "hello" + message[u"message"])
