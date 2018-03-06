from asyncio import get_event_loop

import binascii

from Crypto.Cipher import AES
from axolotl.kdf.hkdfv3 import HKDFv3
from axolotl.util.byteutil import ByteUtil
from base64 import b64decode
from concurrent.futures import ThreadPoolExecutor

from functools import partial
from io import BytesIO

from webwhatsapi import factory_message
from . import WhatsAPIDriver


class WhatsAPIDriverAsync:

    def __init__(self, client="firefox", username="API", proxy=None, command_executor=None, loadstyles=False,
                 profile=None, headless=False, logger=None, extra_params=None, loop=None):

        self._driver = WhatsAPIDriver(client=client, username=username, proxy=proxy, command_executor=command_executor,
                                      loadstyles=loadstyles, profile=profile, headless=headless, logger=logger,
                                      autoconnect=False, extra_params=extra_params)

        self.loop = loop or get_event_loop()
        self._pool_executor = ThreadPoolExecutor(max_workers=1)

    async def get_local_storage(self):
        return await self.loop.run_in_executor(self._pool_executor, self._driver.get_local_storage)

    async def set_local_storage(self, data):
        return await self.loop.run_in_executor(self._pool_executor, self._driver.set_local_storage, data)

    async def save_firefox_profile(self, remove_old=False):
        return await self.loop.run_in_executor(self._pool_executor,
                                               partial(self._driver.set_local_storage,
                                                       remove_old=remove_old))

    async def connect(self):
        return await self.loop.run_in_executor(self._pool_executor, self._driver.connect)

    async def wait_for_login(self):
        return await self.loop.run_in_executor(self._pool_executor, self._driver.wait_for_login)

    async def get_qr(self):
        return await self.loop.run_in_executor(self._pool_executor, self._driver.get_qr)

    async def screenshot(self, filename):
        return await self.loop.run_in_executor(self._pool_executor, self._driver.screenshot, filename)

    async def get_contacts(self):
        return await self.loop.run_in_executor(self._pool_executor, self._driver.get_contacts)

    async def get_all_chats(self):
        return await self.loop.run_in_executor(self._pool_executor, self._driver.get_all_chats)

    # TODO: Check if deprecated
    async def reset_unread(self):
        return await self.loop.run_in_executor(self._pool_executor, self._driver.reset_unread)

    async def get_unread(self, include_me=False, include_notifications=False):
        return await self.loop.run_in_executor(self._pool_executor,
                                               partial(self._driver.get_unread,
                                                       include_me=include_me,
                                                       include_notifications=include_notifications))

    async def get_all_messages_in_chat(self, chat, include_me=False, include_notifications=False):
        return await self.loop.run_in_executor(self._pool_executor,
                                               partial(self._driver.get_all_messages_in_chat,
                                                       chat=chat, include_me=include_me,
                                                       include_notifications=include_notifications))

    async def get_contact_from_id(self, contact_id):
        return await self.loop.run_in_executor(self._pool_executor, self._driver.get_contact_from_id, contact_id)

    async def get_chat_from_id(self, chat_id):
        return await self.loop.run_in_executor(self._pool_executor, self._driver.get_chat_from_id, chat_id)

    async def get_chat_from_phone_number(self, number):
        return await self.loop.run_in_executor(self._pool_executor,
                                               self._driver.get_chat_from_phone_number, number)

    async def reload_qr(self):
        return await self.loop.run_in_executor(self._pool_executor, self._driver.reload_qr)

    async def get_status(self):
        return await self.loop.run_in_executor(self._pool_executor, self._driver.get_status)

    async def contact_get_common_groups(self, contact_id):
        groups = await self.loop.run_in_executor(self._pool_executor,
                                                 self._driver.wapi_functions.getCommonGroups,
                                                 contact_id)
        for group in groups:
            yield group

    async def chat_send_message(self, chat_id, message):
        return await self.loop.run_in_executor(self._pool_executor,
                                               partial(self._driver.chat_send_message,
                                                       chat_id=chat_id, message=message))

    async def chat_get_messages(self, chat_id, include_me=False, include_notifications=False):
        message_objs = await self.loop.run_in_executor(self._pool_executor,
                                                       self._driver.wapi_functions.getAllMessagesInChat,
                                                       chat_id, include_me, include_notifications)
        for message in message_objs:
            yield factory_message(message, self._driver)

    async def chat_load_earlier_messages(self, chat_id):
        return await self.loop.run_in_executor(self._pool_executor,
                                               self._driver.chat_load_earlier_messages,
                                               chat_id)

    async def chat_load_all_earlier_messages(self, chat_id):
        return await self.loop.run_in_executor(self._pool_executor,
                                               self._driver.chat_load_all_earlier_messages, chat_id)

    async def group_get_participants_ids(self, group_id):
        return await self.loop.run_in_executor(self._pool_executor,
                                               self._driver.group_get_participants_ids,
                                               group_id)

    async def group_get_participants(self, group_id):
        participant_ids = await self.group_get_participants_ids(group_id)

        for participant_id in participant_ids:
            yield await self.get_contact_from_id(participant_id)

    async def group_get_admin_ids(self, group_id):
        return await self.loop.run_in_executor(self._pool_executor,
                                               self._driver.group_get_admin_ids,
                                               group_id)

    async def group_get_admins(self, group_id):
        admin_ids = await self.group_get_admin_ids(group_id)

        for admin_id in admin_ids:
            yield await self.get_contact_from_id(admin_id)

    async def download_file(self, url):
        return await self.loop.run_in_executor(self._pool_executor,
                                               self._driver.download_file,
                                               url)

    async def download_media(self, media_msg):
        try:
            if media_msg.content:
                return BytesIO(b64decode(self.content))
        except AttributeError:
            pass

        file_data = await self.download_file(media_msg.client_url)

        media_key = b64decode(media_msg.media_key)
        derivative = HKDFv3().deriveSecrets(media_key,
                                            binascii.unhexlify(media_msg.crypt_keys[media_msg.type]),
                                            112)

        parts = ByteUtil.split(derivative, 16, 32)
        iv = parts[0]
        cipher_key = parts[1]
        e_file = file_data[:-10]

        AES.key_size = 128
        cr_obj = AES.new(key=cipher_key, mode=AES.MODE_CBC, IV=iv)

        return BytesIO(cr_obj.decrypt(e_file))

    async def quit(self):
        return await self.loop.run_in_executor(self._pool_executor, self._driver.quit)

