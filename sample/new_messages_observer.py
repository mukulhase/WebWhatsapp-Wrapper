import os
import sys
import time

from webwhatsapi import WhatsAPIDriver


def run():
    print("Environment", os.environ)
    try:
        os.environ["SELENIUM"]
    except KeyError:
        print("Please set the environment variable SELENIUM to Selenium URL")
        sys.exit(1)

    driver = WhatsAPIDriver(client="remote", command_executor=os.environ["SELENIUM"])
    print("Waiting for QR")
    driver.wait_for_login()
    print("Bot started")

    driver.subscribe_new_messages(NewMessageObserver())
    print("Waiting for new messages...")

    """ Locks the main thread while the subscription in running """
    while True:
        time.sleep(60)


class NewMessageObserver:
    def on_message_received(self, new_messages):
        for message in new_messages:
            if message.type == "chat":
                print(
                    "New message '{}' received from number {}".format(
                        message.content, message.sender.id
                    )
                )
            else:
                print(
                    "New message of type '{}' received from number {}".format(
                        message.type, message.sender.id
                    )
                )


if __name__ == "__main__":
    run()
