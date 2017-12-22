# [WIP] WhatsAPI (Based on web.whatsapp)

## What is it?
This package is used to provide a python interface for interacting with WhatsAPP Web to send and recieve Whatsapp messages.


## Installation

##### Dependencies
You will need to install [Gecko Driver](https://github.com/mozilla/geckodriver) separately, if using firefox, which is the default.

#### From Source
- Clone the repository
- Use `pip install -r requirements.txt' to install the required packages.

#### From PyPI
- Install from pip

`pip install webwhatsapi`

## Usage
- Import library

` from webwhatsapi import WhatsAPIDriver `

- Instantiate driver and set username

` driver = WhatsAPIDriver(username="mkhase", client="firefox", proxy=None) `

- Use the get_qrcode() function to save the QR code in a file, for remote clients, so that you can access them easily. Scan the QR code either from the file, or directly from the client to log in.

` driver.get_qr() `

In case the QR code expires, you can use the reload_qr function to reload it

` driver.reload_qr() `

- And now, the fun part, sending messages.

` driver.send_to_phone_number(phonenumber, message) `

- Viewing unread messages

` driver.view_unread() `

- Callback on receiving messages, used for bots. This feature will be added in the upcoming commit.

## Use Cases
- Auto Reply bot for whatsapp, “I am away from phone”
- Can use whatsapp on phone and this api at the same time, (unlike the other whatsapp APIs, since this uses web.whatsapp)
- No need for number registration
- Hackathons, very easy to setup a whatsapp messaging service.
- API for custom bot making
- Whatsapp cloud(A service):-
-- User can access and send messages from anywhere without scanning qr anymore, just simple user login and password

## Limitation
Phone has to be ON and connected to the internet
