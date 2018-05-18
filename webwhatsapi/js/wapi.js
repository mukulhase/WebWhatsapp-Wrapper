/**
 * This script contains WAPI functions that need to be run in the context of the webpage
 */


window.WAPI = {
    lastRead: {}
};

window.WAPI._serializeRawObj = (obj) => {
    if (obj) {
        return obj.toJSON();
    }
    return {}
};

/**
 * Serializes a chat object
 *
 * @param rawChat Chat object
 * @returns {{}}
 */

window.WAPI._serializeChatObj = (obj) => {
    if (obj == undefined) {
        return null;
    }

    return Object.assign(window.WAPI._serializeRawObj(obj), {
        kind: obj.kind,
        isGroup: obj.isGroup,
        contact: obj['contact']? window.WAPI._serializeContactObj(obj['contact']): null,
        groupMetadata: obj["groupMetadata"]? window.WAPI._serializeRawObj(obj["groupMetadata"]): null,
        presence: obj["presence"]? window.WAPI._serializeRawObj(obj["presence"]):null,
        msgs: null
    });
};

window.WAPI._serializeContactObj = (obj) => {
    if (obj == undefined) {
        return null;
    }

    return Object.assign(window.WAPI._serializeRawObj(obj), {
        formattedName: obj.formattedName,
        isHighLevelVerified: obj.__x_isHighLevelVerified,
        isMe: obj.isMe,
        isMyContact: obj.isMyContact,
        isPSA: obj.isPSA,
        isUser: obj.isUser,
        isVerified: obj.isVerified,
        isWAContact: obj.isWAContact,
        profilePicThumbObj: obj.profilePicThumb ? WAPI._serializeRawObj(obj.profilePicThumb):{},
        statusMute: obj.statusMute,
        msgs: null
    });
};

window.WAPI._serializeMessageObj = (obj) => {
    if (obj == undefined) {
        return null;
    }

    return Object.assign(window.WAPI._serializeRawObj(obj), {
        id: obj.id._serialized,
        sender: obj["senderObj"]?WAPI._serializeContactObj(obj["senderObj"]): null,
        timestamp: obj["t"],
        content: obj["body"],
        isGroupMsg: obj.isGroupMsg,
        isLink: obj.isLink,
        isMMS: obj.isMMS,
        isMedia: obj.isMedia,
        isNotification: obj.isNotification,
        isPSA: obj.isPSA,
        type: obj.type,
        chat: WAPI._serializeChatObj(obj['chat']),
        chatId: obj.id.remote,
        quotedMsgObj: WAPI._serializeMessageObj(obj['_quotedMsgObj']),
        mediaData: window.WAPI._serializeRawObj(obj['mediaData'])
    });
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
    const chats = Store.Chat.models.map((chat) => WAPI._serializeChatObj(chat));

    if (done !== undefined) {
        done(chats);
    } else {
        return chats;
    }
};

/**
 * Fetches all chat IDs from store
 *
 * @param done Optional callback function for async execution
 * @returns {Array|*} List of chat id's
 */
window.WAPI.getAllChatIds = function (done) {
    const chatIds = Store.Chat.models.map((chat) => chat.id);

    if (done !== undefined) {
        done(chatIds);
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

window.WAPI.getChatById = function (id, done) {
    let found = window.WAPI.getChat(id);
    if (found) {
        found = WAPI._serializeChatObj(found);
    } else {
        found = false;
    }

    if (done !== undefined) {
        done(found);
    } else {
        return found;
    }
};


/**
 * I return all unread messages from an asked chat and mark them as read.
 *
 * :param id: chat id
 * :type  id: string
 *
 * :param includeMe: indicates if user messages have to be included
 * :type  includeMe: boolean
 *
 * :param includeNotifications: indicates if notifications have to be included
 * :type  includeNotifications: boolean
 *
 * :param done: callback passed by selenium
 * :type  done: function
 *
 * :returns: list of unread messages from asked chat
 * :rtype: object
 */
window.WAPI.getUnreadMessagesInChat = function (
    id, includeMe, includeNotifications, done
)
{
    // get chat and its messages
    let chat = WAPI.getChat(id);
    let messages = chat.msgs.models;

    // initialize result list
    let output = [];

    // look for unread messages, newest is at the end of array
    for (let i = messages.length - 1; i >= 0; i--)
    {
        // system message: skip it
        if (i === "remove") {
            continue;
        }

        // get message
        let messageObj = messages[i];

        // found a read message: stop looking for others
        if (!messageObj.__x_isNewMsg) {
                break;
        }
		messageObj.__x_isNewMsg = false;
        // process it
        let message = WAPI.processMessageObj(messageObj,
                                             includeMe,
                                             includeNotifications);
		
        // save processed message on result list
        if (message) output.push(message);
    }

    // callback was passed: run it
    if (done !== undefined) {
        done(output);
    }

    // return result list
    return output;
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
        } else if (done) {
            done();
        }
    };
    x();
};

window.WAPI.asyncLoadAllEarlierMessages = function (id, done) {
    done();
    window.WAPI.loadAllEarlierMessages(id);
};

window.WAPI.areAllMessagesLoaded = function (id, done) {
    const found = Store.Chat.models.find((chat) => chat.id === id);
    if (!found.msgs.msgLoadState.__x_noEarlierMsgs) {
        if (done) {
            done(false);
        } else {
            return false
        }
    }
    if (done) {
        done(true);
    } else {
        return true
    }
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
    if (messageObj.isNotification) {
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

window.WAPI.getAllMessageIdsInChat = function (id, includeMe, includeNotifications, done) {
    const chat = WAPI.getChat(id);
    let output = [];
    const messages = chat.msgs.models;
    for (const i in messages) {
        if ((i === "remove")
                || (!includeMe && messages[i].isMe)
                || (!includeNotifications && messages[i].isNotification)) {
            continue;
        }
        output.push(messages[i].id._serialized);
    }
    if (done !== undefined) {
        done(output);
    } else {
        return output;
    }
};

window.WAPI.getMessageById = function (id, done) {
    try {
        Store.Msg.find(id).then((item) => done(WAPI.processMessageObj(item, true, true)))
    } catch (err) {
        done(false);
    }
};

window.WAPI.ReplyMessage = function (idMessage,message,done) {
	var messageObject = Store.Msg.find(idMessage);
	if(messageObject===undefined){
		if (done !== undefined) {
			done(false);
			return false;
		} else {
			return false;
		}
	}
	messageObject = messageObject.value();
	const Chats = Store.Chat.models;

    for (const chat in Chats) {
        if (isNaN(chat)) {
            continue;
        }

        let temp = {};
        temp.name = Chats[chat].__x__formattedTitle;
        temp.id = Chats[chat].__x_id;
        if (temp.id === messageObject.chat.id) {
            if (done !== undefined) {
                Chats[chat].sendMessage(message,null,messageObject).then(function () {
                    function sleep(ms) {
                      return new Promise(resolve => setTimeout(resolve, ms));
                    }

                    var trials = 0;

                    function check() {
                        for (let i=Chats[chat].msgs.models.length - 1; i >= 0; i--) {
                            let msg = Chats[chat].msgs.models[i];

                            if (!msg.senderObj.isMe || msg.body != message) {
                                continue;
                            }
                            done(WAPI._serializeMessageObj(msg));
                            return True;
                        }
                        trials += 1;
                        console.log(trials);
                        if (trials > 30) {
                            done(true);
                            return;
                        }
                        sleep(500).then(check);
                    }
                    check();
                });
                return true;
            } else {
                Chats[chat].sendMessage(message,null,messageObject);
                return true;
            }
        }
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
                    function sleep(ms) {
                      return new Promise(resolve => setTimeout(resolve, ms));
                    }

                    var trials = 0;

                    function check() {
                        for (let i=Chats[chat].msgs.models.length - 1; i >= 0; i--) {
                            let msg = Chats[chat].msgs.models[i];

                            if (!msg.senderObj.isMe || msg.body != message) {
                                continue;
                            }
                            done(WAPI._serializeMessageObj(msg));
                            return True;
                        }
                        trials += 1;
                        console.log(trials);
                        if (trials > 30) {
                            done(true);
                            return;
                        }
                        sleep(500).then(check);
                    }
                    check();
                });
                return true;
            } else {
                Chats[chat].sendMessage(message);
                return true;
            }
        }
    }
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


window.WAPI.getUnreadMessages = function (includeMe, includeNotifications, use_unread_count, done) {
    const chats = Store.Chat.models;
    let output = [];
    for (let chat in chats) {
        if (isNaN(chat)) {
            continue;
        }

        let messageGroupObj = chats[chat];
        let messageGroup = WAPI._serializeChatObj(messageGroupObj);
        messageGroup.messages = [];

        const messages = messageGroupObj.msgs.models;
        for (let i = messages.length - 1; i >= 0; i--) {
            let messageObj = messages[i];
            if (messageObj.__x_isNewMsg || messageObj.__x_MustSent) {
                let message = WAPI.processMessageObj(messageObj, includeMe, includeNotifications);
                if(message){
                    messageObj.__x_isNewMsg = false;
                    messageObj.__x_MustSent = false;
                    messageGroup.messages.unshift(message);
                }
            } else {
                break;
            }
        }

        if (messageGroup.messages.length > 0) {
            output.push(messageGroup);
        } else { // no messages with isNewMsg true
            if (use_unread_count) {
                let n = messageGroupObj.__x_unreadCount; // will use unreadCount attribute to fetch last n messages from sender
                for (let i = messages.length - 1; i >= 0; i--) {
                    let messageObj = messages[i];
                    if (n > 0) {
                        if (!messageObj.__x_isSentByMe) {
                            let message = WAPI.processMessageObj(messageObj, includeMe, includeNotifications);
                            messageGroup.messages.unshift(message);
                            n -= 1;
                        }
                    } else if (n === -1) { // chat was marked as unread so will fetch last message as unread
                        if (!messageObj.__x_isSentByMe) {
                            let message = WAPI.processMessageObj(messageObj, includeMe, includeNotifications);
                            messageGroup.messages.unshift(message);
                            break;
                        }
                    } else { // unreadCount = 0
                        break;
                    }
                }
                if (messageGroup.messages.length > 0) {
                    messageGroupObj.__x_unreadCount = 0; // reset unread counter
                    output.push(messageGroup);
                }
            }
        }

    }
    if (done !== undefined) {
        done(output);
    }
    return output;
};

window.WAPI.markDefaultUnreadMessages = function (done) {
    const chats = Store.Chat.models;
    let output = [];
    for (let chat in chats) {
        if (isNaN(chat)) {
            continue;
        }

        let messageGroupObj = chats[chat];
        let messageGroup = WAPI._serializeChatObj(messageGroupObj);
        messageGroup.messages = [];

        const messages = messageGroupObj.msgs.models;
        for (let i = messages.length - 1; i >= 0; i--) {
            let messageObj = messages[i];
            if (messageObj.__x_isSentByMe) {
                break;
            } else {
                messageObj.__x_MustSent = true;
            }
        }
    }
    if (done !== undefined) {
        done();
    }
    return true;
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

window.WAPI.getBatteryLevel = function (done) {
    let output = Store.Conn.__x_battery;
    if (done !== undefined) {
        done(output);
    }
    return output;
};

window.WAPI.leaveGroup = function (groupId, done) {
    Store.Wap.leaveGroup(groupId);
    if (done !== undefined) {
        done();
    }
    return true;
};

window.WAPI.deleteConversation = function (chatId, done) {
    let conversation = Store.Chat.models.find((chat) => chat.id === chatId);
    let lastReceivedKey = conversation.__x_lastReceivedKey;
    Store.Wap.sendConversationDelete(chatId, lastReceivedKey).then(
        function(response){
            if (done !== undefined) {
                done(response.status);
            }
        }
    );

    return true;
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

