import os, sys, time, json
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.message import Message, MediaMessage

print "Environment", os.environ
try:
   os.environ["SELENIUM"]
except KeyError:
   print "Please set the environment variable SELENIUM to Selenium URL"
   sys.exit(1)

driver = WhatsAPIDriver(client='remote', command_executor=os.environ["SELENIUM"])
print("Waiting for QR")
driver.wait_for_login()
print("Bot started")

while True:
    time.sleep(3)
    print 'Checking for more messages, status', driver.get_status()
    for contact in driver.get_unread():
        for message in contact.messages:
            print(json.dumps(message.get_js_obj(), indent = 4))
            print 'class', message.__class__.__name__
            print 'message', message
            print 'id', message.id
            print 'type', message.type
            print 'timestamp', message.timestamp
            print 'chat_id', message.chat_id
            print 'sender', message.sender
            print 'sender.id', message.sender.id
            print 'sender.safe_name', message.sender.get_safe_name()
            if message.type == 'chat':
                print '-- Chat'
                print 'safe_content', message.safe_content
                print 'content', message.content
                # contact.chat.send_message(message.safe_content)
            elif message.type == 'image' or message.type == 'video' :
                print '-- Image or Video'
                print 'filename', message.filename
                print 'size', message.size
                print 'mime', message.mime
                print 'caption', message.caption
                print 'client_url', message.client_url
                message.save_media('./')
            else:
                print '-- Other'
