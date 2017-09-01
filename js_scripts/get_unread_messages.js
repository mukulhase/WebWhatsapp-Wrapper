const chats = Store.Chat.models;

if (!("last_read" in window)) {
    window.last_read = {};
    for (let chat in chats) {
        // if (isNaN(chat)) {
        //     continue;
        // }

        window.last_read[chats[chat].__x_formattedTitle] = Math.floor(Date.now() / 1000);
    }
}

let Output = [];

for (let chat in chats) {
    if (isNaN(chat)) {
        continue;
    }

    let messageGroupObj = chats[chat];

    let message_group = {};
    message_group.name = messageGroupObj.__x_formattedTitle;
    message_group.id = messageGroupObj.__x_id;
    message_group.isGroup = messageGroupObj.iGroup;
    message_group.messages = [];

    const messages = messageGroupObj.msgs.models;
    for (let i = messages.length - 1; i >= 0; i--) {
        let messageObj = messages[i];

        if (messageObj.__x_t <= last_read[messageGroupObj.__x_formattedTitle] || messageObj.id.fromMe === true) {
            break;
        } else {
            let authorObj = messageObj.__x_authorObj;
            let sender = {};
            sender.name = authorObj.__x_formattedTitle;
            sender.id = authorObj.__x_id;

            let message = {};
            message.content = messageObj.__x_body;
            message.timestamp = messageObj.__x_t;
            message.sender = sender;

            message_group.messages.push(message);
        }
    }

    last_read[messageGroupObj.__x_formattedTitle] = Math.floor(Date.now() / 1000);

    if (message_group.messages.length > 0) {
        Output.push(message_group);
    }
}

return Output;
