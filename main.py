import sqlite3
import re
from telethon import TelegramClient, events
from telethon.sync import TelegramClient
from telethon.tl.types import MessageFwdHeader
from telethon.tl.types.messages import ChatsSlice
from  data import api_id, api_hash, api_client, channels

#Создание базы данных
connection = sqlite3.connect('database.db')

cursor = connection.cursor()  

cursor.execute("""CREATE TABLE IF NOT EXISTS database(
    user_id INTEGER,
    text TEXT,
    date DATE,
    price INTEGER,
    URL TEXT,
    sharp TEXT);
    """)
connection.commit()


#Создание клиента
client = TelegramClient('Me', api_id, api_hash)
client.start()

#Ждем новые сообщение
@client.on(events.NewMessage)

#Обработка сообщений
async def event_handler(event):
    if event.chat.username in channels:
       chat = await event.get_input_chat() #Данные канала из которого пришло сообщение
       msg = await client.get_messages(chat.channel_id, limit = 1) #Последние сообщение
       await client.forward_messages(api_client, msg)  #Отправка сообщения на свой канал

    #Вывод сообщений в базу данный
    cursor.execute('DELETE FROM database')
    async for message in client.iter_messages(chat, reverse = True):
        text = message.text
        user_id = message.id
        date = message.date
        hashtag = str()
        tags = re.findall(r'(#\w+)', str(text))
        for i in range(0,len(tags)):
            hashtag = hashtag + tags[i] + ' '
        #result = re.split(r"\s+", str(text))
        cursor.execute('INSERT INTO database (user_id, text, date, sharp) VALUES (?, ?, ?, ?)', (user_id, text, date, hashtag))
    connection.commit()



client.run_until_disconnected()

