# [WIP] WhatsAPI (Based on web.whatsapp)

## What is it?
This package is used to provide a python interface for interacting with WhatsAPP Web to send and recieve Whatsapp messages.


## Installation

#### From Source
- Clone the Repo
- Use `pip install -r requirements.txt' to install the required packages.

#### From PyPI
- Star the repo :)
- Install from pip

`pip install webwhatsapi`

You will need to install [Gecko Driver](https://github.com/mozilla/geckodriver) separately, if using firefox, which is the default.


## Usage:
- Import library

` from webwhatsapi import WhatsAPIDriver `

- Instantiate driver and set username

` driver = WhatsAPIDriver("mkhase") `

- If the module is to be used as part of a script, and you need an image of the QR code, run the firstrun method. This saves the QR as username.png in, stored in the same directory after running command.

` driver.firstrun() `

If not, you can skip the above step, and directly scan the QR with your phone from the opened Firefox Tab.

- And now, the fun part, sending messages.

` driver.send_to_phone_number(phonenumber, message) `

- Viewing unread messages

` driver.view_unread() `

- Callback on receiving messages

For scripting, to set a function to be called whenever a message is received, use the create_callback method, and pass as the only argument, a function. The function must accept an argument, which is the received messages as a list.

## TODO:
- Add 'get profile picture' accessor

## Use Cases:
- Auto Reply bot for whatsapp, “I am away from phone”
- Can use whatsapp on phone and this api at the same time, (unlike the other whatsapp APIs, since this uses web.whatsapp)
- No need for number registration
- Hackathons, very easy to setup a whatsapp messaging service.
- API for custom bot making
- Whatsapp cloud( A service):-
-- User can access and send messages from anywhere without scanning qr anymore, just simple user login and password

` Limitation:- Phone has to be ON and connected to the internet `


This is the README file for the project.
