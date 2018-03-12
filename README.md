
# WebWhatsAPI (Based on web.whatsapp.com)

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

#### From pipenv
- Install from pipenv
`pipenv install`

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

## Code Documentation
http://mukulhase.github.io/WebWhatsAPI/index.html

## Limitation
Phone has to be on and connected to the internet

# Capabilities
 - Read recent messages
 - Get unread messages
 - Send text messages
 - Get List of Contacts
 - Get List of Groups
 - Get information about Groups
 - Get various events. For example: Leaving, Joining, Missed Call etc.
 - Download media messages
 - Get List of common groups
 - Asyncio driver version

## Note:
There are issues with asynchronous calls in Chrome. Primary support of this api is for firefox. If something doesn't work in chrome, please try firefox.
### Known issues with chrome:
 - Group Metadata
 
### For more queries, contact: mukulhase@gmail.com


## Contribute
Contributing is simple as cloning, making changes and submitting a pull request.
If you would like to contribute, here are a few starters:
- Bug Hunts
- More sorts of examples
- Additional features/ More integrations (This api has the minimum amount, but I don't mind having more data accessible to users)
- Create an env/vagrant box to make it easy for others to contribute. (At the moment, all I have is a requirements.txt
- Phantom JS support

