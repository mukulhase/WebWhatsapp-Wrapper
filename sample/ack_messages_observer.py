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

    driver = WhatsAPIDriver(client='remote', command_executor=os.environ["SELENIUM"])
    print("Waiting for QR")
    driver.wait_for_login()
    print("Bot started")

    driver.subscribe_ack_messages(AckMessageObserver())
    print("Waiting for ack messages...")

    """ Locks the main thread while the subscription in running """
    while True:
        time.sleep(60)


class AckMessageObserver:
    def on_message_ack_change(self, ack_messages):
        for message in ack_messages:
            print("message ack '{}' changed from number {}".format(message.ack, message.sender.id))


if __name__ == '__main__':
    run()
