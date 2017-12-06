contact = arguments[0];
result = Store.Contact.models.filter(
    function(obj){
        name = obj.__x_formattedName;
        if(typeof name === 'string' || name instanceof String) {
            return (name.search(contact) == 0);
        }
        else{
            return false;
        }
    });

result = result.map(function(obj){
    return {
        name: obj.__x_formattedName,
        id: obj.__x_id
    }
});
return result;