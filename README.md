<img alt="Logo" src="https://github.com/Tobaloidee/WebWhatsapp-Wrapper/blob/master/docs/logo/logotype-a-04.png">

## (Based on web.whatsapp.com)
[![PyPI version](https://badge.fury.io/py/webwhatsapi.svg)](https://badge.fury.io/py/webwhatsapi)
[![Firefox version](https://img.shields.io/badge/Firefox-58.0.2-green.svg)]()
[![All Contributors](https://img.shields.io/badge/all_contributors-0-orange.svg?style=flat-square)](#contributors)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## What is it?
This package is used to provide a python interface for interacting with WhatsAPP Web to send and receive Whatsapp messages.
It is based on the official Whatsapp Web Browser Application and uses Selenium browser automation to communicate with Whatsapp Web.

## How to contribute?
[If you are new, click here](docs/contribution_guide.md)

## Local installation

##### Dependencies
You will need to install [Gecko Driver](https://github.com/mozilla/geckodriver) separately, if using firefox, which is the default.

#### From Source
- Clone the repository
- Use `pip install -r requirements.txt` to install the required packages
- or `pipenv install && pipenv install --dev`

#### From PyPI
- Install from pip
`pip install webwhatsapi`

## Docker and remote Selenium Installation

It may be favorable to run Selenium and the webwhatsapi client as Docker containers. This almost completely avoids any installation problems and any messy local installation or dependency hell. The result is a more stable runtime environment for the client, which could run on a headless server.
Using Docker may also help in developing the library itself.

### 1. Create network

    docker network create selenium

### 2. Run Selenium grid/standalone container

This is based on the official Selenium image (https://github.com/SeleniumHQ/docker-selenium).
The following Docker command runs a Selenium standalone Firefox browser in debug (VNC) mode. You can use VNC on port 5900 to view the browser. It uses the network "selenium" and the container is named "firefox" for later reference.

    docker run -d -p 4444:4444 -p 5900:5900 --name firefox --network selenium -v /dev/shm:/dev/shm selenium/standalone-firefox-debug:3.14.0-curium

### 3. Build python/webwhatsapi docker base image

The following command uses the dockerfile to build a new image based on Python 2.7 with all required packages from requirements.txt. 

    docker build -t webwhatsapi .

### 4. Run client container

Now to the client container. The following command installs a local webwhatsapi inside the base container and runs a client. It maps the local directory to the app directory inside the container for easy development. Also sets the network to "selenium" and an environment variable for the remote selenium url. Please note that the remote Selenium hostname must be identical to the name of the Selenium container. 

    docker run --network selenium -it -e SELENIUM='http://firefox:4444/wd/hub' -v $(pwd):/app  webwhatsapi /bin/bash -c "pip install ./;pip list;python sample/remote.py"
    
    
For Windows (cmd):

    docker run --network selenium -it -e SELENIUM='http://firefox:4444/wd/hub' -v "%cd%:/app" webwhatsapi /bin/bash -c "pip install ./;pip list;python sample/remote.py"

For Windows (PowerShell):

    docker run --network selenium -it -e SELENIUM='http://firefox:4444/wd/hub' -v "$(pwd):/app".ToLower() webwhatsapi /bin/bash -c "pip install ./;pip list;python sample/remote.py"

It is also certainly possible to fully build the docker image in advance and define an entrypoint/cmd inside the dockerfile to run a full client.

## Usage

See sample directory for more complex usage examples.

### 1. Import library

    from webwhatsapi import WhatsAPIDriver

### 2. Instantiate driver and set username

    driver = WhatsAPIDriver(username="mkhase")

Possible arguments for constructor:

- client : Type of browser. The default is Firefox, but Chrome and Remote is supported too. See sample directory for remote examples.
- username : Can be any value.
- proxy: The proxy server to configure selenium to. Format is "<proxy>:<portnumber>"
- command_executor: Passed directly as an argument to Remote Selenium. Ignore if not using it. See sample directory for remote examples. 
- loadstyles: Default is False. If True, it will load the styling in the browser.
- profile: Pass the full path to the profile to load it. Profile folder will be end in ".default". For persistent login, open a normal firefox tab, log in to whatsapp, then pass the profile as an argument.

### 3. Use a function to save the QR code in a file, for remote clients, so that you can access them easily. Scan the QR code either from the file, or directly from the client to log in.

    driver.get_qr()

### 4. In case the QR code expires, you can use the reload_qr function to reload it

    driver.reload_qr()

### 5. Viewing unread messages

    driver.view_unread()

### 6. Viewing all contacts

    driver.get_all_chats()

### 7. To send a message, get a Contact object, and call the send_message function with the message.

    <Contact Object>.send_message("Hello")

### 8. Sending a message to an ID, whether a contact or not.

    driver.send_message_to_id(id, message)

## Code Documentation
https://webwhatsapi.readthedocs.io/en/latest/

## Limitation
Phone needs to manually scan the QR Code from Whatsapp Web. Phone has to be on and connected to the internet.

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

## Note
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

## Legal
This code is in no way affiliated with, authorized, maintained, sponsored or endorsed by WhatsApp or any of its affiliates or subsidiaries. This is an independent and unofficial software. Use at your own risk.

## Contributors

Thanks goes to these wonderful people ([emoji key](https://github.com/kentcdodds/all-contributors#emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/kentcdodds/all-contributors) specification. Contributions of any kind welcome!
