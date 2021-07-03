import sqlite3
from telethon import TelegramClient, events
from telethon.sync import TelegramClient
from telethon.tl.types.messages import ChatsSlice
from  data import api_id, api_hash, api_client, channels

#Создание базы данных
conn = sqlite3.connect('database.db')

cur = conn.cursor()  

cur.execute("""CREATE TABLE IF NOT EXISTS database(
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    text TEXT,
    price INTEGER,
    URL TEXT);
    """)

conn.commit()


#Создание клиента
client = TelegramClient('Me', api_id, api_hash)
client.start()

#Ждем новые сообщение
@client.on(events.NewMessage)

#Обработка сообщений
async def event_handler(event):
    if event.chat.username in channels:
       chat = await event.get_input_chat() #Данные канала из которого пришло сообщение
       msg = await client.get_messages(chat.channel_id, limit=1) #Последние сообщение
       await client.forward_messages(api_client, msg)  #Отправка сообщения на свой канал
    
    async for message in client.iter_messages(chat, reverse=True):
        text = message.text
        user_id = message.id
    cur.execute('INSERT INTO database (user_id, text) VALUES (?, ?)', (user_id, text))
    conn.commit()

client.run_until_disconnected()
