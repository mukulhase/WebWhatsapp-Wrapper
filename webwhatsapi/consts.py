URL = "http://web.whatsapp.com"


class Selectors(object):
    FIRST_RUN = "#wrapper"
    QR_CODE = ".qrcode > img:nth-child(4)"
    MAIN_PAGE = ".app.two"
    CHAT_LIST = ".infinite-list-viewport"
    MESSAGE_LIST = "#main > div > div:nth-child(1) > div > div.message-list"
    UNREAD_MESSAGE_BAR = "#main > div > div:nth-child(1) > div > div.message-list > div.msg-unread"
    SEARCH_BAR = ".input"
    SEARCH_CANCEL = ".icon-search-morph"
    CHATS = ".infinite-list-item"
    CHAT_BAR = "div.input"
    SEND_BUTTON = "button.icon:nth-chld(3)"
    LOAD_HISTORY = ".btn-more"
    UNREAD_BADGE = ".icon-meta"
    UNREAD_CHAT_BANNER = ".message-list"
    RECONNECT_LINK = ".action"
    WHATSAPP_QR_ICON = "span.icon:nth-child(2)"
    QR_RELOADER = ".qr-wrapper-container"


class Classes(object):
    UNREAD_BADGE = "icon-meta"
    MESSAGE_CONTENT = "message-text"
    MESSAGE_LIST = "msg"
