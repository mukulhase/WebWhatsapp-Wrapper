# [WIP] WhatsAPI (Based on web.whatsapp)

## Installation

use `pip install -r requirements.txt' to install the required packages.
You will need to install [Gecko Driver](https://github.com/mozilla/geckodriver) separately, if using firefox, which is the default.

## Usage:
- Import library

` from webwhatsapp import WhatsAPIDriver `

- Instantiate driver and set username

` driver = WhatsAPIDriver("mkhase") `

- If the module is to be used as part of a script, and you need an image of the QR code, run the firstrun method. This saves the QR as username.png in, stored in the same directory after running command.

` driver.firstrun() `

If not, you can skip the above step, and directly scan the QR with your phone.

- And now, the fun part, sending messages.

` driver.send(contact, message,[ entry]) `
OR
` driver.send_to_phone_number(phonenumber, message) `

If the entry parameter is not given, and there are multiple contacts which match the contact argument, they are returned as a list. To choose an entry out of the list, call the function, with the index of the contact as entry argument.

- Viewing unread messages

` driver.view_unread() `

Incase a search for 'contact' yields multiple contacts, the list will be returned. To send the message to a specific person, call the function again, and pass the entry argument, and the message will be sent to that entry on the list

- Callback on receiving messages

For scripting, to set a function to be called whenever a message is received, use the create_callback method, and pass as the only argument, a function. The function must accept an argument, which is the received messages as a list.

## Use Cases:
- Auto Reply bot for whatsapp, “I am away from phone”
- Can use whatsapp on phone and this api at the same time, (unlike the other whatsapp APIs, since this uses web.whatsapp)
- No need for number registration
- Hackathons, very easy to setup a whatsapp messaging service, just simple ajax requests!
- API for custom bot making
- Whatsapp cloud( A service):-
-- User can access and send messages from anywhere without scanning qr anymore, just simple user login and password

` Limitation:- Phone has to be ON and connected to the internet `
