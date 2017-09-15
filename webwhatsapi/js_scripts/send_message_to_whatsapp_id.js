var Chats = Store.Chat.models;
var id = arguments[0];
var message = arguments[1];
for (chat in Chats) {
    if (isNaN(chat)) {
        continue;
    };
    var temp = {};
    temp.contact = Chats[chat].__x__formattedTitle;
    temp.id = Chats[chat].__x_id;
    if(temp.id == id){
        Chats[chat].sendMessage(message);
        return true;
    }
}
return false;