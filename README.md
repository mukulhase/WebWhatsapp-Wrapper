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


## Usage
- Import library

` from webwhatsapi import WhatsAPIDriver `

- Instantiate driver and set username

#### Firefox

` driver = WhatsAPIDriver(username="mkhase") `

#### Chrome

` driver = WhatsAPIDriver(username="mkhase", browser="chrome") `

#### Optional driver instantiation parameters

``` python
# Default value is "API"
username="username"
```
``` python
# Default value is "firefox"
browser="browser" 
```

``` python
# Default value is "None", driver has to be in path or script directory.
driver_executable_path="/Path/to/driver/executable" 
```

- If the module is to be used as part of a script, and you need an image of the QR code, run the firstrun method. This saves the QR as username.png in, stored in the same directory after running command.

` driver.firstrun() `

If not, you can skip the above step, and directly scan the QR with your phone from the opened Firefox Tab.

- And now, the fun part, sending messages.

` driver.send_to_phone_number(phonenumber, message) `

- Viewing unread messages

` driver.view_unread() `

- Callback on receiving messages

For scripting, to set a function to be called whenever a message is received, use the create_callback method, and pass as the only argument, a function. The function must accept an argument, which is the received messages as a list.

## Persistent Webdriver Sessions

#### Using Firefox with Persistent Session

Firefox and Gecko Driver must already be installed and working!

```in: python_interpreter```
1. Run this python code once
``` python
driver = WhatsAPIDriver(browser='Firefox' username='API') """ browser = 'Firefox' is the default setting, \
                                                            so it can be omitted.
                                                            username = 'API' is the default setting, \
                                                            so it can be omitted. """
```
2. Wait until the website is fully loaded but don't scan the QR Code.
3. When loading is done, quit ether using Strg + C on the python interpreter or
4. Just close the browser window.

Now you have a similar directory structure under your ```<project_root>```.
```
.
├── firefox_cache
│   └── API
```

```in: bash, cmd or terminal```
##### Run the Firefox Profile Manager
#### Be sure that no other Firefox Instance is running!
```firefox -ProfileManager``` or ```firefox -P```

```in: Firefox Profile Manager```
* Create a new Profile
* Give it a Name, use your Projectname or Usernameinstance for example.
* Choose Folder ..., select the previous created Folder in the firefox_cache directory
* Goto [Web.WhatsApp.com](https://web.WhatsApp.com) and Scan the QR Code
* Exit Firefox, and run it again. Test if session persistence is working.
* Finish

You can change the new Profile to being the default Firefox Profile, but its should not be
necessary because the Profile Directory gets passed in thru the WhatsAPI Class.

```in: python_interpreter```
##### Run the above python code again

Test if it's working, you should be ready to code now. ;-)

If you have create the ```Cache_directory``` in advance, you can skip the first part.


#### Using Chrome with Persistent Session

Chrome Driver must already be installed and working!

```in: python_interpreter```
1. Run this python code
1. Wait for the website is fully loaded
3. Scan the QR Code
4. When loading is done, quit ether using Strg + C on the python interpreter or
5. Just close the browser window.

```python
driver = WhatsAPIDriver(browser='Chrome' username='API') """ username = 'API' is the default setting, \
                                                            so it can be omitted. """
```                                                            

Now you have a similar directory structure under your ```<project_root>```.
```
.
├── chrome_cache
│   └── API
```
Test if it's working, you should be ready to code now. ;-)

#### Caveats
Chrome Driver doesn't support [BMP](https://bugs.chromium.org/p/chromedriver/issues/detail?id=187) ```Emoji-Unicode-Characters```, so you can't pass them in using the ```Selenium.send_keys()``` Method.


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
