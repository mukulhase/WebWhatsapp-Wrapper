/**
 * This script contains WAPI functions that need to be run in the context of the webpage
 */


window.WAPI = {
    lastRead: {}
};

/**
 * Serializes a raw object
 *
 * Basically just clones the object into a new object
 *
 * We need to clone because a lot of properties are non enumerable but we still need them
 * The cloning operation effectively turns all non enumerable fields into enumerable ones
 *
 * This function naively ignores non primitive types
 *
 * @param rawObj Object to serialize
 * @returns {{}}
 * @private
 */
// window.WAPI._serializeRawObj = function (rawObj) {
//     let obj = {};
//     for (const property in rawObj) {
//         if (rawObj[property] !== Object(rawObj[property])) {
//             obj[property] = rawObj[property];
//         }
//     }
//
//     return obj;
// };

/**
 * Serializes a chat object
 *
 * @param rawChat Chat object
 * @returns {{}}
 */
// window.WAPI.serializeChat = function (rawChat) {
//     let chat = {};
//
//     let name = null;
//     if (rawChat.__x_name !== undefined) {
//         name = rawChat.__x_name;
//     } else {
//         if (rawChat.__x_formattedName !== undefined) {
//             name = rawChat.__x_formattedName;
//         } else {
//             if (rawChat.__x_formattedTitle !== undefined) {
//                 name = rawChat.__x_formattedTitle;
//             }
//         }
//     }
//
//     chat.name = name;
//     chat.id = rawChat.__x_id;
//     chat.isGroup = rawChat.isGroup;
//     chat._raw = WAPI._serializeRawObj(rawChat);
//
//     return chat;
// };

/**
 * Serializes a message object
 *
 * @param rawMessage Message object
 * @param sender Sender object
 * @returns {{}}
 */
// window.WAPI.serializeMessage = function (rawMessage, sender) {
//     let message = {};
//     message.content = rawMessage.__x_body;
//     message.timestamp = rawMessage.__x_t;
//     message.sender = sender;
//     message._raw = WAPI._serializeRawObj(rawMessage);
//
//     return message;
// };

window.WAPI.getAllContacts = function (done) {
    const contacts = Store.Contact.models.map((contact) => contact.all);

    if (done !== undefined) {
        done(contacts);
    } else {
        return contacts;
    }
};

window.WAPI.getContact = function(id, done) {
    const found = Store.Contact.models.find((contact) => contact.id === id);

    if (done !== undefined) {
        done(found);
    } else {
        return found;
    }
};

window.WAPI.getAllChats = function (done) {
    const chats = Store.Chat.models.map((chat) => chat.all);

    if (done !== undefined) {
        done(chats);
    } else {
        return chats;
    }
};

window.WAPI.getChat = function(id, done) {
    const found = Store.Chat.models.find((chat) => chat.id === id);

    if (done !== undefined) {
        done(found);
    } else {
        return found;
    }
};

window.WAPI.getAllGroupMetadata = function() {
    return Store.GroupMetadata.models.map((groupData) => WAPI._serializeRawObj(groupData));
};

/**
 * Gets list of contacts
 *
 * @returns {Array}
 */
window.WAPI.getContacts = function () {
    const contacts = window.Store.Contact.models;

    let output = [];

    for (const contact in contacts) {
        if (contacts[contact].isMyContact === true) {
            output.push(WAPI._serializeRawObj(contacts[contact]));
        }
    }

    return output;
};

/**
 * Gets object representing the logged in user
 *
 * @returns {{}}
 */
window.WAPI.getMe = function () {
    const contacts = window.Store.Contact.models;

    const rawMe = contacts.find((contact, _, __) => contact.__x_formattedName === "You", contacts);

    return WAPI._serializeRawObj(rawMe);
};

window.WAPI._getChat = function (id) {
    const chats = Store.Chat.models;

    return chats.find((contact, _, __) => contact.__x_id === id, chats);
};

window.WAPI.getChat = (id) => WAPI._serializeRawObj(WAPI._getChat(id));

window.WAPI.getAllMessagesInChat = function (id, includeMe) {
    const chat = WAPI._getChat(id);

    let output = [];

    const messages = chat.msgs.models;
    for (const i in messages) {
        if (i === "remove") {
            continue;
        }

        const messageObj = messages[i];

        if (messageObj.__x_isNotification) {
            // System message
            // (i.e. "Messages you send to this chat and calls are now secured with end-to-end encryption...")
            continue;
        }

        if (messageObj.id.fromMe === false || includeMe) {
            let message = WAPI._serializeRawObj(messageObj);

            output.push(message);
        }
    }

    WAPI.lastRead[chat.__x_formattedTitle] = Math.floor(Date.now() / 1000);

    return output;
};

window.WAPI.sendMessage = function (id, message) {
    const Chats = Store.Chat.models;

    for (const chat in Chats) {
        if (isNaN(chat)) {
            continue;
        }

        let temp = {};
        temp.name = Chats[chat].__x__formattedTitle;
        temp.id = Chats[chat].__x_id;
        if (temp.id === id) {
            Chats[chat].sendMessage(message);

            return true;
        }
    }

    return false;
};

window.WAPI.getUnreadMessages = function () {
    const chats = Store.Chat.models;

     WAPI.lastRead = {};
     for (let chat in chats) {
         if (isNaN(chat)) {
             continue;
         }

         WAPI.lastRead[chats[chat].__x_formattedTitle] = Math.floor(Date.now() / 1000);
     }

    let output = [];
    for (let chat in chats) {
        if (isNaN(chat)) {
            continue;
        }

        let messageGroupObj = chats[chat];

        let messageGroup = WAPI.serializeChat(messageGroupObj);
        messageGroup.messages = [];

        const messages = messageGroupObj.msgs.models;
        for (let i = messages.length - 1; i >= 0; i--) {
            let messageObj = messages[i];

            if (messageObj.__x_isNotification) {
                // System message
                // (i.e. "Messages you send to this chat and calls are now secured with end-to-end encryption...")
                continue;
            }

            if (messageObj.__x_t <= WAPI.lastRead[messageGroupObj.__x_formattedTitle] || messageObj.id.fromMe === true) {
                break;
            } else {
                let message = WAPI._serializeRawObj(messageObj);

                messageGroup.messages.push(message);
            }
        }

        WAPI.lastRead[messageGroupObj.__x_formattedTitle] = Math.floor(Date.now() / 1000);

        if (messageGroup.messages.length > 0) {
            output.push(messageGroup);
        }
    }

    return output;
};

window.WAPI._getGroupMetadata = async function (id) {
    const metadata = Store.GroupMetadata.models.find((group, _, __) => group.__x_id === id);

    if (metadata !== undefined) {
        if (metadata.stale) {
            await metadata.update();
        }
    }

    return metadata;
};

window.WAPI._getGroupParticipants = async function(id) {
    const metadata = await WAPI._getGroupMetadata(id);
    return metadata.participants;
};

window.WAPI.getGroupParticipants = async function(id, done) {
    const participants = await WAPI._getGroupParticipants(id);

    const ids = participants.map((participant) => participant.id);

    if (done !== undefined) {
        done(ids);
    } else {
        return ids;
    }
};

window.WAPI.getGroupAdmins = async function(id) {
    const participants = WAPI._getGroupParticipants(id);
    return participants
        .filter((participant) => participant.isAdmin)
        .map((admin) => admin.id);
};

window.WAPI.getGroupOwner = async function(id) {
    return WAPI._getGroupMetadata(id).owner.id;
};

window.WAPI.getCommonGroups = function(id) {
    // return
};

