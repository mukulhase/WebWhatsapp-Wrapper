window.WAPI = {};

window.WAPI.serializeChat = function(rawChat) {
    let chat = {};
    chat.name = rawChat.__x_name;
    chat.id = rawChat.__x_id;
    chat.isGroup = rawChat.isGroup;
    chat._raw = rawChat;

    return chat;
};

window.WAPI.serializeMessage = function(rawMessage, sender) {
    let message = {};
    message.content = rawMessage.__x_body;
    message.timestamp = rawMessage.__x_t;
    message.sender = sender;
    message._raw = rawMessage;

    return message;
};

window.WAPI.getContacts = function() {
    const contacts = window.Store.Contact.models;

    let output = [];

    for (const contact in contacts) {
        if (contact !== "remove" && contacts[contact].isMyContact === true && contacts[contact].__x_name !== "You") {
            output.push(WAPI.serializeChat(contacts[contact]));
        }
    }

    return output;
};