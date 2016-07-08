var Chats = Store.Chat.models;
if (!('last_read' in window)) {
    this.last_read = {};
    for (chat in Chats) {
        window.last_read[Chats[chat]._values.formattedTitle] = Math.floor(Date.now() / 1000);
    }
}
var Output = [];
for (chat in Chats) {
    var temp = {};
    temp.contact = Chats[chat]._values.formattedTitle;
    temp.messages = [];
    var messages = Chats[chat].msgs.models;
    for (var i=messages.length-1;i>=0;i--) {
        console.log(messages[i].id.fromMe);
        if (messages[i]._values.t <= last_read[Chats[chat]._values.formattedTitle] || (messages[i].id.fromMe==true)) {
            break;
        } else {
            temp.messages.push(
                {
                    message: messages[i]._values.body,
                    timestamp: messages[i]._values.t
                }
            );
        }
    }
    last_read[Chats[chat]._values.formattedTitle] = messages[messages.length-1]._values.t;
    if(temp.messages.length>0)
        Output.push(temp);
}
return Output;
