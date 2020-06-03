from asyncio import Task, ensure_future, get_event_loop, sleep, wait
from signal import SIGINT

from webwhatsapi.async_driver import WhatsAPIDriverAsync
from webwhatsapi.objects.message import Message

loop = get_event_loop()

driver = WhatsAPIDriverAsync(loadstyles=True, loop=loop)


async def run():
    await sleep(10, loop=loop)
    print("Connecting...")
    await driver.connect()
    print("Wait for login...")
    await driver.wait_for_login()

    for contact in await driver.get_unread():
        if Task.current_task().cancelled():
            break

        for message in contact.messages:
            if isinstance(message, Message):  # Currently works for text messages only.
                print("Message from {}: {}".format(message.sender, message.content))
                print("Resending...")
                contact.chat.chat_send_message(message.safe_content)
        await sleep(1, loop=loop)

    await driver.quit()


async def start():
    async def heartbeat():
        print("Starting heartbeat...")
        while not Task.current_task().cancelled():
            print("beat!")
            await sleep(0.5, loop=loop)

    fut_heartbeat = ensure_future(heartbeat(), loop=loop)
    fut_runner = ensure_future(run(), loop=loop)

    def stop(*args, **kwargs):
        fut_heartbeat.cancel()
        fut_runner.cancel()

    loop.add_signal_handler(SIGINT, stop)

    await wait([fut_heartbeat, fut_runner], loop=loop)


loop.run_until_complete(start())
