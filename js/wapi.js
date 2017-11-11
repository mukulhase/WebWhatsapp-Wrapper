/**
 * This script contains WAPI functions that need to be run in the context of the webpage
 */


window.WAPI = {
    lastRead: {}
};

/**
 * Fetches all contact objects from store
 *
 * @param done Optional callback function for async execution
 * @returns {Array|*} List of contacts
 */
window.WAPI.getAllContacts = function (done) {
    const contacts = Store.Contact.models.map((contact) => contact.all);

    if (done !== undefined) {
        done(contacts);
    } else {
        return contacts;
    }
};

/**
 * Fetches contact object from store by ID
 *
 * @param id ID of contact
 * @param done Optional callback function for async execution
 * @returns {T|*} Contact object
 */
window.WAPI.getContact = function(id, done) {
    const found = Store.Contact.models.find((contact) => contact.id === id);

    if (done !== undefined) {
        done(found);
    } else {
        return found;
    }
};

/**
 * Fetches all chat objects from store
 *
 * @param done Optional callback function for async execution
 * @returns {Array|*} List of chats
 */
window.WAPI.getAllChats = function (done) {
    const chats = Store.Chat.models.map((chat) => chat.all);

    if (done !== undefined) {
        done(chats);
    } else {
        return chats;
    }
};

/**
 * Fetches chat object from store by ID
 *
 * @param id ID of chat
 * @param done Optional callback function for async execution
 * @returns {T|*} Chat object
 */
window.WAPI.getChat = function(id, done) {
    const found = Store.Chat.models.find((chat) => chat.id === id);

    if (done !== undefined) {
        done(found);
    } else {
        return found;
    }
};

/**
 * Fetches all group metadata objects from store
 *
 * @param done Optional callback function for async execution
 * @returns {Array|*} List of group metadata
 */
window.WAPI.getAllGroupMetadata = function(done) {
    const groupData = Store.GroupMetadata.models.map((groupData) => groupData.all);

    if (done !== undefined) {
        done(groupData);
    } else {
        return groupData;
    }
};

/**
 * Fetches group metadata object from store by ID
 *
 * @param id ID of group
 * @param done Optional callback function for async execution
 * @returns {T|*} Group metadata object
 */
window.WAPI.getGroupMetadata = async function(id, done) {
    let found = Store.GroupMetadata.models.find((groupData) => groupData.id === id);

    if (found !== undefined) {
        if (found.stale) {
            await found.update();
        }
    }

    if (done !== undefined) {
        done(found);
    } else {
        return found;
    }
};

window.WAPI._getGroupParticipants = async function(id) {
    const metadata = await WAPI.getGroupMetadata(id);
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
    const participants = await WAPI._getGroupParticipants(id);
    console.log(participants);
    return participants
        .filter((participant) => participant.isAdmin)
        .map((admin) => admin.id);
};

window.WAPI.getGroupOwner = async function(id) {
    return WAPI._getGroupMetadata(id).owner.id;
};


// FUNCTIONS UNDER THIS LINE ARE UNSTABLE

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

window.WAPI.getCommonGroups = function(id) {
    // return
};

