/*
Experimental !!!

Returns a Python List of Dictonarys for Groupnames and Participants.

[{
    u'Participants':[u'meber1@c.us',u'member2@c.us', ...],
    u'Name': u'Group1'
},{
    u'Participants':[u'meber1@c.us',u'member2@c.us', ...],
    u'Name': u'Group2'
}]

Participant Values gets only populated when the WA Webservice Functions groupMetadataFind, groupMetaDataFindFromPhone
are executed which sends the Query to the Phone using the WA Webservice Method

return m.send2({ data: ["query", GroupMetadata", "phonenumber@c.us"], retryOn5xx: !0})

This can be manually triggered by pressing on a Group within the Webdriver GUI.

Maybe someone could write code to execute the m.send2 Method directly.
 */

var Groups = Store.GroupMetadata.models;

var GroupOutput = [];

for (group in Groups) {
    if (isNaN(group)) {
        continue;
    }

    //if(!(Groups[group].__x_id.toLowerCase().indexOf("@broadcast") >= 0))

    var group_name = ggn(Groups[group].__x_id);

    var i = Store.GroupMetadata.models[group].participants.models;
    var ii = [];

    for (p in i) {
        if (isNaN(group)) {
            continue;
        };
        var n = Store.GroupMetadata.models[group].participants.models[p].__x_id;
        var m = ggn(Store.GroupMetadata.models[group].participants.models[p].__x_id);
        if (n == null){
            continue;
        }
        ii.push(n);

    }
    GroupOutput.push({
        'Group' : {'Name' :group_name, 'Participants' : ii }
    });

}

function ggn(pno) {
    var contacts = window.Store.Contact.models;
        for(var i in contacts){
        if(isNaN(i)) {
            continue;
        }
        if(pno == contacts[i].__x_id){
            return (contacts[i].__x_name);
        }
    }
}
return GroupOutput;
console.log(GroupOutput);
