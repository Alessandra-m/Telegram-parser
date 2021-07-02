import sqlite3
from telethon import TelegramClient, events
from telethon.sync import TelegramClient
from telethon.tl.types.messages import ChatsSlice
from  data import api_id, api_hash, api_client, channels

#Создание базы данных
database = 'database.sqilte'

def create_connect():
    return sqlite3.connect(database)

def init_db():
    with create_connect() as connect:
        connect.execute("""CREATE TABLE IF NOT EXISTS database(
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            price INTEGER,
            URL TEXT);
            """)
        connect.commit()

def add_message(user_id, message):
    with create_connect() as connect:
        connect.execute(
            'INSERT INTO Message (user_id, text) VALUES (?, ?)', (user_id, message)
        )
        connect.commit()

init_db()

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
        print(message.text)

client.run_until_disconnected()