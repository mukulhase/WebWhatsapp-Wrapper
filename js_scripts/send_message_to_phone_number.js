var contact = arguments[0];
var message = arguments[1];

var Chats = Store.Chat.models;

for (chat in Chats) {
    if (isNaN(chat)) {
        continue;
    }

    var temp = {};
    temp.contact = Chats[chat].__x__formattedTitle;
    temp.id = Chats[chat].__x_id;
    if (temp.id.indexOf(contact) != -1 && temp.id.indexOf("g.us") == -1) {
        Chats[chat].sendMessage(message);

        return true;
    }
}

return false;