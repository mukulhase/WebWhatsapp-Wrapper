import os, sys, time, json, datetime
from webwhatsapi import WhatsAPIDriver
from webwhatsapi.objects.message import Message, MediaMessage

# EXAMPLE OF LOGGER BOT
# =====================
# Logs everything that passes through the phone, and saves media content too.
# Perfect companion for those who hate the ones who use to "erase message".
# The bot interacts with a remote phone, called "master".
# This phone can send simple commands and receives periodic notifications
# in order to know the bot is still running

# Global Const
# cc = country code, e.g. for UK '44'
# ppp = mobile prefix
# nnnnnnn = mobile number
masters_number = "ccpppnnnnnnn"

# Global Vars
pinger = -1
now = datetime.datetime.now()
start_time = datetime.datetime.now()

# Procs and Funcs
def print_and_log(text):
    print(text)
    f = open("generallog.log", "a+", encoding="utf-8")
    f.write(
        "[{timestamp}] : {txt}\n".format(timestamp=datetime.datetime.now(), txt=text)
    )
    f.close()


def send_message_to_master(message):
    phone_safe = masters_number  # Phone number with country code
    phone_whatsapp = "{}@c.us".format(phone_safe)  # WhatsApp Chat ID
    driver.send_message_to_id(phone_whatsapp, message)


def process_command(command):
    print_and_log("Processing command: {cmd}".format(cmd=command))
    if command.lower() == "status":
        send_message_to_master("I am still alive")
    elif command.lower() == "quit":
        quit()
    elif command.lower() == "ping":
        send_message_to_master("The counter is now {ping}".format(ping=pinger))
    elif command.lower() == "uptime":
        uptime = datetime.datetime.now() - start_time
        send_message_to_master(
            "Up since {start}, hence for a total time of {upt} by now".format(
                start=start_time, upt=uptime
            )
        )
    else:
        send_message_to_master(
            "I am sorry but I can't understand '{cmd}'".format(cmd=command)
        )


# Main
driver = WhatsAPIDriver()
print("Waiting for QR")

driver.wait_for_login()
print("Bot started")
start_time = datetime.datetime.now()

try:

    while True:
        time.sleep(3)  # Checks for new messages every 3 secs.
        pinger = pinger + 1
        if (pinger % 600) == 0:  # Notification every 30 min. (600 * 3 sec = 1800 sec)
            pinger = 0
            send_message_to_master(
                "Resetting counter to {pingcount}. Driver status is '{status}'".format(
                    pingcount=pinger, status=driver.get_status()
                )
            )
        print(
            "Checking for more messages, status. Pinger={pingcount}".format(
                pingcount=pinger
            ),
            driver.get_status(),
        )
        for contact in driver.get_unread(include_me=True, include_notifications=True):
            for message in contact.messages:
                print(json.dumps(message.get_js_obj(), indent=4))
                # Log full JSON to general log
                f = open("generallog.log", "a+", encoding="utf-8")
                f.write(
                    "\n\n==========================================================================\nMessage received at {timestamp}\n".format(
                        timestamp=str(datetime.datetime.now())
                    )
                )
                try:
                    f.write(json.dumps(message.get_js_obj(), indent=4))
                except:
                    f.write("ERROR!! Unprintable JSON!")
                    send_message_to_master("Unprintable JSON! Please check!")
                f.write("\n")
                f.close()
                print("class", message.__class__.__name__)
                print("message", message)
                print("id", message.id)
                print("type", message.type)
                print("timestamp", message.timestamp)
                print("chat_id", message.chat_id)
                print("sender", message.sender)

                # Notifications don't seem to have sender.id neither sender.getsafename()
                try:
                    sender_id = message.sender.id
                except:
                    sender_id = "NONE"
                print("sender.id", sender_id)
                try:
                    sender_safe_name = message.sender.get_safe_name()
                except:
                    sender_safe_name = "NONE"
                print("sender.safe_name", sender_safe_name)

                if message.type == "chat":
                    print("-- Chat")
                    print("safe_content", message.safe_content)
                    try:
                        print("content", message.content)
                    except:
                        print(
                            "content is unsafe! Printing safe_content instead",
                            message.safe_content,
                        )
                        send_message_to_master(
                            "Unprintable MESSAGE CONTENT! Please check!"
                        )
                    f = open(
                        "chat_" + message.chat_id["_serialized"] + ".chat.log",
                        "a+",
                        encoding="utf-8",
                    )
                    f.write(
                        "[ {sender} | {timestamp} ] ".format(
                            sender=message.sender.get_safe_name(),
                            timestamp=message.timestamp,
                        )
                    )
                    try:
                        f.write(message.content)
                    except:
                        f.write(
                            "(safecontent) {content}".format(
                                content=message.safe_content
                            )
                        )
                    f.write("\n")
                    f.close()
                    f = open(
                        "safechat_" + message.chat_id["_serialized"] + ".chat.log", "a+"
                    )
                    f.write(
                        "[ {sender} | {timestamp} ] {content}\n".format(
                            sender=message.sender.get_safe_name(),
                            timestamp=message.timestamp,
                            content=message.safe_content,
                        )
                    )
                    f.close()
                    if message.sender.id["user"] == masters_number:
                        print_and_log(
                            "Message from master: '{cmd}'.".format(cmd=message.content)
                        )
                        process_command(message.content)
                elif (
                    message.type == "image"
                    or message.type == "video"
                    or message.type == "document"
                    or message.type == "audio"
                ):
                    print("-- Media")
                    print("filename", message.filename)
                    print("size", message.size)
                    print("mime", message.mime)
                    msg_caption = ""
                    if hasattr(message, "caption"):
                        msg_caption = message.caption
                        print("caption", message.caption)
                    print("client_url", message.client_url)
                    f = open(
                        "chat_" + message.chat_id["_serialized"] + ".chat.log", "a+"
                    )
                    f.write(
                        "[ {sender} | {timestamp} ] sent media chat_{id}\{filename} with caption '{caption}'\n".format(
                            sender=message.sender.get_safe_name(),
                            timestamp=message.timestamp,
                            id=message.chat_id["_serialized"],
                            filename=message.filename,
                            caption=msg_caption,
                        )
                    )
                    f.close()
                    f = open(
                        "safechat_" + message.chat_id["_serialized"] + ".chat.log", "a+"
                    )
                    f.write(
                        "[ {sender} | {timestamp} ] sent media chat_{id}\{filename} with caption '{caption}'\n".format(
                            sender=message.sender.get_safe_name(),
                            timestamp=message.timestamp,
                            id=message.chat_id["_serialized"],
                            filename=message.filename,
                            caption=msg_caption,
                        )
                    )
                    f.close()
                    if not os.path.exists(
                        "chat_{id}".format(id=message.chat_id["_serialized"])
                    ):
                        os.makedirs(
                            "chat_{id}".format(id=message.chat_id["_serialized"])
                        )
                    message.save_media(
                        "chat_{id}".format(id=message.chat_id["_serialized"])
                    )
                else:
                    print("-- Other")
except Exception as e:
    print("EXCEPTION:", e)
    send_message_to_master("I am dying! HELP!\n")
    send_message_to_master("Exception was: {exc}\n".format(exc=e))
    f = open("generallog.log", "a+", encoding="utf-8")
    f.write("\n\nEXCEPTION: {exc}\n".format(exc=e))
    f.close
    raise
