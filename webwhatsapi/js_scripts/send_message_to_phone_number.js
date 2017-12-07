var Chats = Store.Chat.models;
var contact = arguments[0];
var message = arguments[1];

var user = Store.Contact.models.find(function(e) {
    if(e.isUser == true) {
        return e.__x_id.search(contact) != -1
    }
});

if(!user) return;

Store.Chat.add({ id: user.__x_id, }, { merge: true, add: true, });

for (chat in Chats) {
    if (isNaN(chat) || Chats[chat].__x_id.indexOf(contact) == -1) {
        continue;
    };

    var temp = {};
    temp.contact = Chats[chat].__x_formattedTitle;
    temp.id = Chats[chat].__x_id;
    if(temp.id.search(contact)!=-1 && temp.id.search('g.us')==-1 ){
        Chats[chat].sendMessage(message);
        return true
    }
}

return false;
