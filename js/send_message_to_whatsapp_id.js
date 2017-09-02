const id = arguments[0];
const message = arguments[1];

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