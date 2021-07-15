import binascii
from asyncio import CancelledError, get_event_loop, sleep
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger

import aiohttp
from axolotl.kdf.hkdfv3 import HKDFv3
from axolotl.util.byteutil import ByteUtil
from base64 import b64decode
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from functools import partial
from io import BytesIO
from selenium.common.exceptions import TimeoutException

from . import WhatsAPIDriver

logger = getLogger(__name__)


class WhatsAPIDriverAsync:
    def __init__(
        self,
        client="firefox",
        username="API",
        proxy=None,
        command_executor=None,
        loadstyles=False,
        profile=None,
        headless=False,
        logger=None,
        extra_params=None,
        loop=None,
    ):

        self._driver = WhatsAPIDriver(
            client=client,
            username=username,
            proxy=proxy,
            command_executor=command_executor,
            loadstyles=loadstyles,
            profile=profile,
            headless=headless,
            logger=logger,
            autoconnect=False,
            extra_params=extra_params,
        )

        self.loop = loop or get_event_loop()
        self._pool_executor = ThreadPoolExecutor(max_workers=1)

    async def _run_async(self, method, *args, **kwargs):
        try:
            logger.debug("Running async method {}".format(method.__name__))
            fut = self.loop.run_in_executor(
                self._pool_executor, partial(method, *args, **kwargs)
            )
            return await fut
        except CancelledError:
            fut.cancel()
            raise

    async def get_local_storage(self):
        return await self._run_async(self._driver.get_local_storage)

    async def set_local_storage(self, data):
        return await self._run_async(self._driver.set_local_storage, data)

    async def save_firefox_profile(self, remove_old=False):
        return await self._run_async(
            self._driver.save_firefox_profile, remove_old=remove_old
        )

    async def connect(self):
        return await self._run_async(self._driver.connect)

    async def wait_for_login(self, timeout=90):
        for _ in range(timeout // 2):
            try:
                return await self._run_async(self._driver.wait_for_login, timeout=1)
            except TimeoutException:
                await sleep(1)
        raise TimeoutException("Timeout: Not logged")

    async def get_qr(self):
        return await self._run_async(self._driver.get_qr)

    async def screenshot(self, filename):
        return await self._run_async(self._driver.screenshot, filename)

    async def get_contacts(self):
        return await self._run_async(self._driver.get_contacts)

    async def get_all_chats(self):
        for chat_id in await self.get_all_chat_ids():
            yield await self.get_chat_from_id(chat_id)

    async def get_all_chat_ids(self):
        return await self._run_async(self._driver.get_all_chat_ids)

    async def get_unread(
        self, include_me=False, include_notifications=False, use_unread_count=False
    ):
        return await self._run_async(
            self._driver.get_unread,
            include_me=include_me,
            include_notifications=include_notifications,
            use_unread_count=use_unread_count,
        )

    async def get_all_messages_in_chat(
        self, chat, include_me=False, include_notifications=False
    ):
        return await self._run_async(
            self._driver.get_all_messages_in_chat,
            chat=chat,
            include_me=include_me,
            include_notifications=include_notifications,
        )

    async def get_contact_from_id(self, contact_id):
        return await self._run_async(self._driver.get_contact_from_id, contact_id)

    async def get_chat_from_id(self, chat_id):
        return await self._run_async(self._driver.get_chat_from_id, chat_id)

    async def get_chat_from_phone_number(self, number):
        return await self._run_async(self._driver.get_chat_from_phone_number, number)

    async def reload_qr(self):
        return await self._run_async(self._driver.reload_qr)

    async def get_status(self):
        return await self._run_async(self._driver.get_status)

    async def check_number_status(self, number_id):
        return await self._run_async(self._driver.check_number_status, number_id)

    async def contact_get_common_groups(self, contact_id):
        groups = await self._run_async(
            self._driver.contact_get_common_groups(contact_id), contact_id
        )
        for group in groups:
            yield group

    async def chat_send_message(self, chat_id, message):
        return await self._run_async(
            self._driver.chat_send_message, chat_id=chat_id, message=message
        )

    async def chat_get_messages(
        self, chat, include_me=False, include_notifications=False
    ):
        async for msg_id in self.get_all_message_ids_in_chat(
            chat, include_me=include_me, include_notifications=include_notifications
        ):
            yield self.get_message_by_id(msg_id)

    async def get_all_message_ids_in_chat(
        self, chat, include_me=False, include_notifications=False
    ):
        message_ids = await self._run_async(
            self._driver.get_all_message_ids_in_chat,
            chat,
            include_me,
            include_notifications,
        )
        for i in message_ids:
            yield i

    async def get_message_by_id(self, message_id):
        return await self._run_async(self._driver.get_message_by_id, message_id)

    async def chat_load_earlier_messages(self, chat_id):
        return await self._run_async(self._driver.chat_load_earlier_messages, chat_id)

    async def chat_load_all_earlier_messages(self, chat_id):
        return await self._run_async(
            self._driver.chat_load_all_earlier_messages, chat_id
        )

    async def async_chat_load_all_earlier_messages(self, chat_id):
        return await self._run_async(
            self._driver.async_chat_load_all_earlier_messages, chat_id
        )

    async def are_all_messages_loaded(self, chat_id):
        return await self._run_async(self._driver.are_all_messages_loaded, chat_id)

    async def group_get_participants_ids(self, group_id):
        return await self._run_async(self._driver.group_get_participants_ids, group_id)

    async def group_get_participants(self, group_id):
        participant_ids = await self.group_get_participants_ids(group_id)

        for participant_id in participant_ids:
            yield await self.get_contact_from_id(participant_id)

    async def group_get_admin_ids(self, group_id):
        return await self._run_async(self._driver.group_get_admin_ids, group_id)

    async def group_get_admins(self, group_id):
        admin_ids = await self.group_get_admin_ids(group_id)

        for admin_id in admin_ids:
            yield await self.get_contact_from_id(admin_id)

    async def download_file(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.read()

    async def download_media(self, media_msg, force_download=False):
        if not force_download:
            try:
                if media_msg.content:
                    return BytesIO(b64decode(media_msg.content))
            except AttributeError:
                pass

        file_data = await self.download_file(media_msg.client_url)

        media_key = b64decode(media_msg.media_key)
        derivative = HKDFv3().deriveSecrets(
            media_key, binascii.unhexlify(media_msg.crypt_keys[media_msg.type]), 112
        )

        parts = ByteUtil.split(derivative, 16, 32)
        iv = parts[0]
        cipher_key = parts[1]
        e_file = file_data[:-10]

        cr_obj = Cipher(
            algorithms.AES(cipher_key), modes.CBC(iv), backend=default_backend()
        )
        decryptor = cr_obj.decryptor()
        return BytesIO(decryptor.update(e_file) + decryptor.finalize())

    async def quit(self):
        return await self._run_async(self._driver.quit)
