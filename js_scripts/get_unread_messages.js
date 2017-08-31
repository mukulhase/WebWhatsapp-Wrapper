const Chats = Store.Chat.models;

if (!("last_read" in window)) {
    window.last_read = {};
    for (let chat in Chats) {
        // if (isNaN(chat)) {
        //     continue;
        // }

        window.last_read[Chats[chat].__x_formattedTitle] = Math.floor(Date.now() / 1000);
    }
}

let Output = [];

for (let chat in Chats) {
    // if (isNaN(chat)) {
    //     continue;
    // }

    let temp = {};
    temp.contact = Chats[chat].__x_formattedTitle;
    temp.id = Chats[chat].__x_id;
    temp.messages = [];
    const messages = Chats[chat].msgs.models;
    for (let i = messages.length - 1; i >= 0; i--) {
        if (messages[i].__x_t <= last_read[Chats[chat].__x_formattedTitle] || messages[i].id.fromMe === true) {
            console.log("no");
            break;
        } else {
            console.log("yes");
            temp.messages.push(
                {
                    message: messages[i].__x_body,
                    timestamp: messages[i].__x_t
                }
            );
        }
    }
    last_read[Chats[chat].__x_formattedTitle] = Math.floor(Date.now() / 1000);
    if (temp.messages.length > 0)
        Output.push(temp);
}

console.log("hi", Output);
return Output;