# [WIP] WhatsAPI (Based on web.whatsapp)

##Usage:
- Import library

` from WhatsAPI.webwhatsapp import WhatsAPIDriver `

- Instantiate driver and set username

` driver = WhatsAPIDriver(username="mkhase") `

- Scan QR (username.png stored in the same directory after running command)

` driver.firstrun() `

- And now, the fun part, sending messages

` driver.send_message(contact, message,[ entry]) `

- Viewing unread messages

` driver.view_unread() `

Incase a search for 'contact' yields multiple contacts, the list will be returned. To send the message to a specific person, call the function again, and pass the entry argument, and the message will be sent to that entry on the list


##Use Cases:
- Auto Reply bot for whatsapp, “I am away from phone”
- Can use Phone whatsapp's at the same time, (unlike the other whatsapp APIs)
- No need for number registration
- Hackathons, very easy to setup a whatsapp messaging service, just simple ajax requests!
- API for custom bot making
- Whatsapp cloud( A service):-
-- User can access and send messages from anywhere without scanning qr anymore, just simple user login and password

` Limitation:- Phone has to be ON and connected to the internet `
