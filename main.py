from telethon import TelegramClient, events
from data import api_id, api_hash, api_client, channels

client = TelegramClient('Me', api_id, api_hash)
client.start()

@client.on(events.NewMessage)
async def event_handler(event):
    if event.chat.username in channels:
       chat = await event.get_input_chat()
       msg = await client.get_messages(chat.channel_id, limit=1)
       await client.forward_messages(api_client, msg)
       

client.run_until_disconnected()