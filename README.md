# [WIP] WhatsAPI (Based on web.whatsapp)

## What is it?
This package is used to provide a python interface for interacting with WhatsAPP Web to send and receive Whatsapp messages.


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
1. Import library
` from webwhatsapi import WhatsAPIDriver `

2. Instantiate driver and set username
` driver = WhatsAPIDriver(username="mkhase") `
Possible arguments for constructor:
    - client : Type of browser. The default is Firefox, but Chrome and Remote is supported too.
    - username : Can be any value.
    - proxy: The proxy server to configure selenium to. Format is "<proxy>:<portnumber>"
    - command executor: Passed directly as an argument to Remote Selenium. Ignore if not using it.
    - loadstyle: Default is true. If true, doesn't load the styling in the browser.
	- profile: Pass the full path to the profile to load it. Profile folder will be end in ".default". For persistent login, open a normal firefox tab, log in to whatsapp, then pass the profile as an argument.


3. Use the get_qrcode() function to save the QR code in a file, for remote clients, so that you can access them easily. Scan the QR code either from the file, or directly from the client to log in.
` driver.get_qr() `

4. In case the QR code expires, you can use the reload_qr function to reload it
` driver.reload_qr() `

5. Viewing unread messages
` driver.view_unread() `

6. Viewing all contacts
` driver.get_all_chats() `

7. To send a message, get a Contact object, and call the send_message function with the message.
`<Contact Object>.send_message("Hello")`

## Use Cases
- Auto Reply bot for whatsapp, “I am away from phone”
- Can use whatsapp on phone and this api at the same time, (unlike the other whatsapp APIs, since this uses web.whatsapp)
- No need for number registration
- Hackathons, very easy to setup a whatsapp messaging service.
- API for custom bot making
- Whatsapp cloud(A service): User can access and send messages from anywhere without scanning qr anymore, just simple user login and password

## Limitation
Phone has to be on and connected to the internet

