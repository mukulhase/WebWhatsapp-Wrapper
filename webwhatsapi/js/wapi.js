/**
 * This script contains WAPI functions that need to be run in the context of the webpage
 */


window.WAPI = {
    lastRead: {}
};


/**
 * Serializes a chat object
 *
 * @param rawChat Chat object
 * @returns {{}}
 */
window.WAPI.serializeChat = (obj) => ({
    name: obj.__x_name || obj.__x_formattedName || obj.__x_formattedTitle || "None",
    id: obj.__x_id,
    isGroup: obj.isGroup,
    kind: obj.kind,
});

window.WAPI._serializeRawObj = (obj) => {
    return obj.all;
};

window.WAPI._serializeContactObj = (obj) => ({
    formattedName: obj.__x_formattedName,
    formattedShortName: obj.__x_formattedShortName,
    shortName: obj.__x_formattedShortName,
    formattedShortNameWithNonBreakingSpaces: obj.__x_formattedShortNameWithNonBreakingSpaces,
    formattedUser: obj.__x_formattedUser,
    id: obj.__x_id,
    isHighLevelVerified: obj.__x_isHighLevelVerified,
    isMe: obj.__x_isMe,
    isMyContact: obj.__x_isMyContact,
    isPSA: obj.__x_isPSA,
    isUser: obj.__x_isUser,
    isVerified: obj.__x_isVerified,
    isWAContact: obj.__x_isWAContact,
    name: obj.__x_name,
    profilePicThumb: obj.__x_profilePicThumb ? obj.__x_profilePicThumb.__x_imgFull : "none",
    statusMute: obj.__x_statusMute,
    pushname: obj.__x_pushname
});

window.WAPI._serializeNotificationObj = (obj) => ({
    sender: obj["senderObj"] ? WAPI._serializeContactObj(obj["senderObj"]) : false,
    isGroupMsg: obj.__x_isGroupMsg,
    content: obj["body"],
    isLink: obj.__x_isLink,
    isMMS: obj.__x_isMMS,
    isMedia: obj.__x_isMedia,
    isNotification: obj.__x_isNotification,
    timestamp: obj["t"],
    type: obj.__x_type,
    subtype: obj.__x_subtype,
    recipients: obj.__x_recipients,
});

//TODO: Add chat ref
window.WAPI._serializeMessageObj = (obj) => ({
    sender: WAPI._serializeContactObj(obj["senderObj"]),
    timestamp: obj["t"],
    content: obj["body"],
    isGroupMsg: obj.__x_isGroupMsg,
    isLink: obj.__x_isLink,
    isMMS: obj.__x_isMMS,
    isMedia: obj.__x_isMedia,
    isNotification: obj.__x_isNotification,
    isPSA: obj.__x_isPSA,
    type: obj.__x_type,
    size: obj.__x_size,
    mime: obj.__x_mimetype,
});

/**
 * Fetches all contact objects from store
 *
 * @param done Optional callback function for async execution
 * @returns {Array|*} List of contacts
 */
window.WAPI.getAllContacts = function (done) {
    const contacts = Store.Contact.models.map((contact) => WAPI._serializeContactObj(contact));

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
window.WAPI.getContact = function (id, done) {
    const found = Store.Contact.models.find((contact) => contact.id === id);

    if (done !== undefined) {
        done(window.WAPI._serializeContactObj(found));
    } else {
        return window.WAPI._serializeContactObj(found);
    }
};

/**
 * Fetches all chat objects from store
 *
 * @param done Optional callback function for async execution
 * @returns {Array|*} List of chats
 */
window.WAPI.getAllChats = function (done) {
    const chats = Store.Chat.models.map((chat) => WAPI.serializeChat(chat));

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
window.WAPI.getChat = function (id, done) {
    const found = Store.Chat.models.find((chat) => chat.id === id);
    if (done !== undefined) {
        done(found);
    } else {
        return found;
    }
};

/**
 * Load more messages in chat object from store by ID
 *
 * @param id ID of chat
 * @param done Optional callback function for async execution
 * @returns None
 */
window.WAPI.loadEarlierMessages = function (id, done) {
    const found = Store.Chat.models.find((chat) => chat.id === id);
    if (done !== undefined) {
        found.loadEarlierMsgs().then(function(){done()});
    } else {
        found.loadEarlierMsgs();
    }
};

/**
 * Load more messages in chat object from store by ID
 *
 * @param id ID of chat
 * @param done Optional callback function for async execution
 * @returns None
 */
// window.WAPI.recurseLoad = function (found, done){
//     if(!found.msgs.msgLoadState.__x_noEarlierMsgs){
//         found.loadEarlierMessages().then(window.WAPI.recurse);
//     }else {
//         done();
//     }
// };

window.WAPI.loadAllEarlierMessages = function (id, done) {
    const found = Store.Chat.models.find((chat) => chat.id === id);
    x = function(){
        if(!found.msgs.msgLoadState.__x_noEarlierMsgs){
            found.loadEarlierMsgs().then(x);
        }else {
            done();
        }
    };
    x();
};


/**
 * Fetches all group metadata objects from store
 *
 * @param done Optional callback function for async execution
 * @returns {Array|*} List of group metadata
 */
window.WAPI.getAllGroupMetadata = function (done) {
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
window.WAPI.getGroupMetadata = async function (id, done) {
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

/**
 * Fetches group participants
 *
 * @param id ID of group
 * @returns {Promise.<*>} Yields group metadata
 * @private
 */
window.WAPI._getGroupParticipants = async function (id) {
    const metadata = await WAPI.getGroupMetadata(id);
    return metadata.participants;
};

/**
 * Fetches IDs of group participants
 *
 * @param id ID of group
 * @param done Optional callback function for async execution
 * @returns {Promise.<Array|*>} Yields list of IDs
 */
window.WAPI.getGroupParticipantIDs = async function (id, done) {
    const participants = await WAPI._getGroupParticipants(id);
    const ids = participants.map((participant) => participant.id);

    if (done !== undefined) {
        done(ids);
    } else {
        return ids;
    }
};

window.WAPI.getGroupAdmins = async function (id) {
    const participants = await WAPI._getGroupParticipants(id);
    return participants
        .filter((participant) => participant.isAdmin)
        .map((admin) => admin.id);
};

/**
 * Gets object representing the logged in user
 *
 * @returns {Array|*|$q.all}
 */
window.WAPI.getMe = function (done) {
    const contacts = window.Store.Contact.models;

    const rawMe = contacts.find((contact) => contact.all.isMe, contacts);

    if (done !== undefined) {
        done(rawMe.all);
    } else {
        return rawMe.all;
    }
    return rawMe.all;
};

window.WAPI.processMessageObj = function (messageObj, includeMe, includeNotifications) {
    if (messageObj.__x_isNotification) {
        if(includeNotifications)
            return WAPI._serializeNotificationObj(messageObj);
        else return;
        // System message
        // (i.e. "Messages you send to this chat and calls are now secured with end-to-end encryption...")
    } else if (messageObj.id.fromMe === false || includeMe) {
        return WAPI._serializeMessageObj(messageObj);
    }
    return;
};

window.WAPI.getAllMessagesInChat = function (id, includeMe, includeNotifications, done) {
    const chat = WAPI.getChat(id);
    let output = [];
    const messages = chat.msgs.models;
    for (const i in messages) {
        if (i === "remove") {
            continue;
        }
        const messageObj = messages[i];
        let message = WAPI.processMessageObj(messageObj, includeMe, includeNotifications)
        if (message)output.push(message);
    }
    if (done !== undefined) {
        done(output);
    } else {
        return output;
    }
};

window.WAPI.sendMessage = function (id, message, done) {
    const Chats = Store.Chat.models;

    for (const chat in Chats) {
        if (isNaN(chat)) {
            continue;
        }

        let temp = {};
        temp.name = Chats[chat].__x__formattedTitle;
        temp.id = Chats[chat].__x_id;
        if (temp.id === id) {
            if (done !== undefined) {
                Chats[chat].sendMessage(message).then(function () {
                    done(true);
                });
                return true;
            } else {
                Chats[chat].sendMessage(message);
                return true;
            }
        }
    }
    if (done !== undefined) {
        done();
    } else {
        return false;
    }
    return false;
};

function isChatMessage(message) {
    if (message.__x_isSentByMe) {
        return false;
    }
    if (message.__x_isNotification) {
        return false;
    }
    if (!message.__x_isUserCreatedType) {
        return false;
    }
    return true;
}


window.WAPI.getUnreadMessages = function (includeMe, includeNotifications, done) {
    const chats = Store.Chat.models;
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
            if (!messageObj.__x_isNewMsg) {
                break;
            } else {
                messageObj.__x_isNewMsg = false;
                let message = WAPI.processMessageObj(messageObj, includeMe,  includeNotifications);
                if(message){
                    messageGroup.messages.push(message);
                }
            }
        }

        if (messageGroup.messages.length > 0) {
            output.push(messageGroup);
        }
    }
    if (done !== undefined) {
        done(output);
    } else {
        return output;
    }
    return output;
};

window.WAPI.getGroupOwnerID = async function (id) {
    return WAPI.getGroupMetadata(id).owner.id;
};

// FUNCTIONS UNDER THIS LINE ARE UNSTABLE

window.WAPI.getCommonGroups = function (id) {
    // return
};
