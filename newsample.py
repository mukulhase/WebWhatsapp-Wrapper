#!/usr/bin/env python2
from WhatsappAPI import WhatsappAPI
from pprint import pprint
from Socket import Socket
from numeroHelper import NumeroHelper
from Decrypter import Decrypter
from Ssh import Ssh

print "waiting for QR"
WhatsappAPI = WhatsappAPI()
print "bot started"

Decrypter = Decrypter()
caminhoDownload = "C:\\temp"
tipo = 1

def getExt(type, filename = None):
    global tipo
    if type == "image":
        tipo = 2
        return ".jpeg"
    if type == "audio" or type == "ptt":
        tipo = 3
        return ".wma"
    if type == "video":
        tipo = 4
        return ".mp4"
    if type == "document":
        tipo = 5
        if filename is not None:
            return "." + filename.split(".")[-1]
    return None

while True:
    mensagens = WhatsappAPI.getMensagens()
    for jid in mensagens.keys():
        if jid in mensagens:
            nomeContato = mensagens[jid]['contato']
            mensagensContato = mensagens[jid][u'messages']
            for mensagem in mensagensContato:
                tipo = 1
                idMensagem = mensagem[u'id']
                conteudoMensagem = mensagem[u'message']
                timestamp = mensagem[u'timestamp']
                telefoneContato = NumeroHelper.toNumeroFutorofone(jid)
                type = mensagem[u'type']

                if type == "location":
                    lat = mensagem[u'lat']
                    lng = mensagem[u'lng']
                    conteudoMensagem = lat + " " + lng

                if mensagem[u'clientUrl'] is not None:
                    url = mensagem[u'clientUrl']
                    mediaKey = mensagem[u'mediaKey']
                    filename = mensagem[u'filename']

                    filename = idMensagem + getExt(type, filename)
                    conteudoMensagem = filename

                    Decrypter.getMediaContent(url, mediaKey, type)
                    Decrypter.salvar(caminhoDownload + filename)
                    #conteudoMensagem = Decrypter.getBase64File()

                print "---------------------------------------------"
                print "nomeContato: "
                print nomeContato
                print "telefoneContato: "
                print telefoneContato
                print "idMensagem: "
                print idMensagem
                print "tipo: "
                print tipo
                print "conteudoMensagem: "
                print conteudoMensagem
                print "---------------------------------------------"
