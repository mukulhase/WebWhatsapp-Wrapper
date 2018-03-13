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

window.WAPI._serializeContactObj = (obj) => (obj?{
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
}:null);

//TODO: Add chat ref
window.WAPI._serializeMessageObj = function(obj) {

    let data = {
        sender: WAPI._serializeContactObj(obj["senderObj"]),
        id: obj.id._serialized,
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
        chatId: obj.__x_id.remote
    };

    if (data.isMedia || data.isMMS) {
        data['clientUrl'] = obj['__x_clientUrl'];
        data['mediaKey'] = obj['__x_mediaKey'];
        data['mediaData'] = {
            duration: obj['__x_mediaData']['__x_duration'],
            filehash: obj['__x_mediaData']['__x_filehash'],
            mimetype: obj['__x_mediaData']['__x_mimetype'],
            encriptationKey: obj['__x_mediaData']['__x_encryptionKey'],
            fullHeight: obj['__x_mediaData']['__x_fullHeight'],
            fullWidth: obj['__x_mediaData']['__x_fullWidth'],
            size: obj['__x_mediaData']['__x_size'],
        }
    }

    if (data.isNotification) {
        data['subtype']= obj.__x_subtype;
        data['recipients']= obj.__x_recipients;
    }

    return data;
};
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
 * Fetches all contact objects from store, filters them
 *
 * @param done Optional callback function for async execution
 * @returns {Array|*} List of contacts
 */
window.WAPI.getMyContacts = function (done) {
    const contacts = Store.Contact.models.filter(d => d.__x_isMyContact === true).map((contact) => WAPI._serializeContactObj(contact));

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
 * Fetches all groups objects from store
 *
 * @param done Optional callback function for async execution
 * @returns {Array|*} List of chats
 */
window.WAPI.getAllGroups = function (done) {
    const groups = window.WAPI.getAllChats().filter((chat) => chat.isGroup);

    if (done !== undefined) {
        done(groups);
    } else {
        return groups;
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

window.WAPI.loadAllEarlierMessages = function (id, done) {
    const found = Store.Chat.models.find((chat) => chat.id === id);
    x = function(){
        if (!found.msgs.msgLoadState.__x_noEarlierMsgs){
            found.loadEarlierMsgs().then(x);
        } else {
            done();
        }
    };
    x();
};

/**
 * Load more messages in chat object from store by ID till a particular date
 *
 * @param id ID of chat
 * @param lastMessage UTC timestamp of last message to be loaded
 * @param done Optional callback function for async execution
 * @returns None
 */

window.WAPI.loadEarlierMessagesTillDate = function (id, lastMessage, done) {
    const found = Store.Chat.models.find((chat) => chat.id === id);
    x = function(){
        if(found.msgs.models[0].t>lastMessage){
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
    let output = Store.GroupMetadata.models.find((groupData) => groupData.id === id);

    if (output !== undefined) {
        if (output.stale) {
            await output.update();
        }
    }

    if (done !== undefined) {
        done(output);
    }
    return output;

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
    const output = (await WAPI._getGroupParticipants(id))
        .map((participant) => participant.id);

    if (done !== undefined) {
        done(output);
    }
    return output;
};

window.WAPI.getGroupAdmins = async function (id, done) {
    const output = (await WAPI._getGroupParticipants(id))
        .filter((participant) => participant.isAdmin)
        .map((admin) => admin.id);

    if (done !== undefined) {
        done(output);
    }
    return output;
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
            return WAPI._serializeMessageObj(messageObj);
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

window.WAPI.sendMessageToID = function (id, message, done) {
    if(Store.Chat.models.length == 0)
        return false;

    var originalID = Store.Chat.models[0].id;
    Store.Chat.models[0].id = id;
    if (done !== undefined) {
        Store.Chat.models[0].sendMessage(message).then(function(){ Store.Chat.models[0].id = originalID; done(true); });
        return true;
    } else {
        Store.Chat.models[0].sendMessage(message);
        Store.Chat.models[0].id = originalID;
        return true;
    }

    if (done !== undefined)
        done();
    else
        return false;

    return true;
}

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


window.WAPI.sendSeen = function (id, done) {
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
                Chats[chat].sendSeen(false).then(function () {
                    done(true);
                });
                return true;
            } else {
                Chats[chat].sendSeen(false);
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
    }
    return output;
};

window.WAPI.getGroupOwnerID = async function (id, done) {
    const output = await WAPI.getGroupMetadata(id).owner.id;
    if (done !== undefined) {
        done(output);
    }
    return output;

};

window.WAPI.getCommonGroups = async function (id, done) {
    let output = [];

    groups = window.WAPI.getAllGroups();

    for (let idx in groups) {
        try {
            participants = await window.WAPI.getGroupParticipantIDs(groups[idx].id);
            if (participants.filter((participant) => participant == id).length) {
                output.push(groups[idx]);
            }
        } catch(err) {
            console.log("Error in group:");
            console.log(groups[idx]);
            console.log(err);
        }
    }

    if (done !== undefined) {
        done(output);
    }
    return output;
};

window.WAPI.downloadFile = function (url, done) {
    let xhr = new XMLHttpRequest();

    xhr.onload = function() {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                let reader = new FileReader();
                reader.readAsDataURL(xhr.response);
                reader.onload =  function(e){
                    done(reader.result.substr(reader.result.indexOf(',')+1))
                };
            } else {
                console.error(xhr.statusText);
            }
        }
    };
    xhr.open("GET", url, true);
    xhr.responseType = 'blob';
    xhr.send(null);
}

