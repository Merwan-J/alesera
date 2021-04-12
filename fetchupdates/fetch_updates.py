from telethon import TelegramClient, events
import logging
import configparser
import os
import socks
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

# config = configparser.ConfigParser()
# config.read('config.ini')

# api_id = config.getint('telegram_api', 'api_id')
# api_hash = config['telegram_api']['api_hash']

PORT = int(os.environ.get('PORT', 5000))

api_id = 3883924
api_hash = '00c46303da8d943ccf5c88f7172efee9'

# , proxy=(socks.HTTP, 'https://fetchupdates.herokuapp.com/', 80)
# , connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
#     proxy=('https://fetchupdates.herokuapp.com/', 80, '00000000000000000000000000000000')
client = TelegramClient('anon', api_id, api_hash)
print(client)


@client.on(events.NewMessage(from_users=(-1001404646371)))
async def my_event_handler(event):
    msg = event.message
    bot_id = 1633317216
    channel_username = 'freelance_ethio'
    await client.forward_messages(bot_id,msg)

   



client.start()
client.run_until_disconnected()
