var contact = arguments[0];
var message = arguments[1];

var user = Store.Contact.models.find(function (e) { return e.__x_id && e.__x_id.search(contact)!=-1 });

if(!user) return;

Store.Chat.add({ id: user.__x_id, }, { merge: true, add: true, });

for (chat in Store.Chat.models) {
    if (isNaN(chat)) {
        continue;
    };
    var temp = {};
    temp.contact = Store.Chat.models[chat].__x_formattedTitle;
    temp.id = Store.Chat.models[chat].__x_id;
    if(temp.id.search(contact)!=-1 && temp.id.search('g.us')==-1 ){
        Store.Chat.models[chat].sendMessage(message);
        return true
    }
}

return false;
