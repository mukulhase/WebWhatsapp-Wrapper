const chats = Store.Chat.models;

if (!("last_read" in window)) {
    window.last_read = {};
    for (let chat in chats) {
        if (isNaN(chat)) {
            continue;
        }

        window.last_read[chats[chat].__x_formattedTitle] = Math.floor(Date.now() / 1000);
    }
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

        if (messageObj.__x_t <= last_read[messageGroupObj.__x_formattedTitle] || messageObj.id.fromMe === true) {
            break;
        } else {
            let sender = WAPI.serializeChat(messageObj.__x_senderObj);
            let message = WAPI.serializeMessage(messageObj, sender);

            messageGroup.messages.push(message);
        }
    }

    last_read[messageGroupObj.__x_formattedTitle] = Math.floor(Date.now() / 1000);

    if (messageGroup.messages.length > 0) {
        output.push(messageGroup);
    }
}

return output;
