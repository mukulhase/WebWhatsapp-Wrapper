window.WAPI = {};

/**
 * Serializes a raw object
 *
 * Selenium likes to strip "private" properties (not sure why)
 * This function adds a wapi_ prefix to all property names so they don't disappear
 *
 * This function naively ignores non primitive types
 *
 * @param rawObj Object to serialize
 * @returns {{}}
 * @private
 */
window.WAPI._serializeRawObj = function(rawObj) {
    let obj = {};
    for (const property in rawObj) {
        if (rawObj[property] !== Object(rawObj[property])) {
            obj["wapi_" + property] = rawObj[property];
        }
    }

    return obj;
};

/**
 * Serializes a chat object
 *
 * @param rawChat Chat object
 * @returns {{}}
 */
window.WAPI.serializeChat = function(rawChat) {
    let chat = {};
    chat.name = rawChat.__x_name;
    chat.id = rawChat.__x_id;
    chat.isGroup = rawChat.isGroup;
    chat._raw = WAPI._serializeRawObj(rawChat);

    return chat;
};

/**
 * Serializes a message object
 *
 * @param rawMessage Message object
 * @param sender Sender object
 * @returns {{}}
 */
window.WAPI.serializeMessage = function(rawMessage, sender) {
    let message = {};
    message.content = rawMessage.__x_body;
    message.timestamp = rawMessage.__x_t;
    message.sender = sender;
    message._raw = WAPI._serializeRawObj(rawMessage);

    return message;
};

/**
 * Gets list of contacts
 *
 * @returns {Array}
 */
window.WAPI.getContacts = function() {
    const contacts = window.Store.Contact.models;

    let output = [];

    for (const contact in contacts) {
        if (contacts[contact].isMyContact === true) {
            output.push(WAPI.serializeChat(contacts[contact]));
        }
    }

    console.log(output[0]._raw);

    return output;
};

/**
 * Gets object representing the logged in user
 *
 * @returns {{}}
 */
window.WAPI.getMe = function() {
    const contacts = window.Store.Contact.models;

    const rawMe = contacts.find((contact, _, __) => contact.__x_formattedName === "You", contacts);
    console.log(rawMe);

    return WAPI.serializeChat(rawMe);
};
