function match(pno, id){
    return lcs(pno, id).length > (pno.length - 2)
}
function lcs(lcstest, lcstarget) {
 matchfound = 0;
 lsclen = lcstest.length;
  for(lcsi=0; lcsi<lcstest.length; lcsi++){
   lscos=0;
    for(lcsj=0; lcsj<lcsi+1; lcsj++){
     re = new RegExp("(?:.{" + lscos + "})(.{" + lsclen + "})", "i");
     temp = re.test(lcstest);
     re = new RegExp("(" + RegExp.$1 + ")", "i");
      if(re.test(lcstarget)){
       matchfound=1;
       result = RegExp.$1;
       break;
       }
     lscos = lscos + 1;w
     }
     if(matchfound==1){return result; break;}
    lsclen = lsclen - 1;
   }
  result = "";
  return result;
 }
function getContactName(pno){
    var contacts = window.Store.Contact.models;
    for(var i in contacts){
        if(i!="remove"){
            if(match(pno,contacts[i]._values.id))
            return [contacts[i]._values.id, contacts[i]._values.name];
        }
    }
    return false;
}