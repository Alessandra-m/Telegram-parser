import sqlite3
import re
import datetime
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
    price TEXT,
    URL TEXT,
    sharp TEXT);
    """)
connection.commit()

#Дата получения сообщений
date = datetime.datetime.today()
last_date = date - datetime.timedelta(days = 180)

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

    async for message in client.iter_messages(chat, reverse = True, offset_date = last_date):
        text = message.text
        user_id = message.id
        date_1 = message.date

        hashtag = str()
        text_str = str(text)
        tags = re.findall(r'(#\w+)', text_str)
        for i in range(0,len(tags)):
            hashtag = hashtag + tags[i] + ' '

        price = str()
        text_str = text_str.lower()

        if re.findall(r'(цена+[ :-]+\d+)', text_str) != []:
            price = re.findall(r'(цена+[ :-]+\d+)', text_str)

        elif  re.findall(r'(\d+[ ]+[т]+[ы]+[c])', text_str) != []:
            price = re.findall(r'(\d+[ ]+[т]+[ы]+[c])', text_str)

        elif re.findall(r'(\d+[т]+[ы]+[c])', text_str) != []:
            price = re.findall(r'(\d+[т]+[ы]+[c])', text_str)

        elif  re.findall(r'(\d+[ ]+[р]+[у]+[б])', text_str) != []:
            price = re.findall(r'(\d+[ ]+[р]+[у]+[б])', text_str)
        
        elif  re.findall(r'(\d+[р]+[у]+[б])', text_str) != []:
            price = re.findall(r'(\d+[р]+[у]+[б])', text_str)

        elif  re.findall(r'(\d+[ ]+[₽рт])', text_str) != []:
            price = re.findall(r'(\d+[ ]+[₽рт])', text_str)

        elif re.findall(r'(\d+[₽рт])', text_str) != []:
            price = re.findall(r'(\d+[₽рт])', text_str)
        
        elif  re.findall(r'(\d+[ ]+[кk]+\Z|[ .])', text_str) != []:
            price = re.findall(r'(\d+[ ]+[кk]+\Z|[ .])', text_str)

        elif re.findall(r'(\d+[кk]+\Z|[ .])', text_str) != []:
            price = re.findall(r'(\d+[кk]+\Z|[ .])', text_str)
        

        res_price = str()
        res_p = str()
        for i in range(0,len(price)):
            res_price = res_price + price[i] + ' '
        res_price = re.findall(r'(\d+)', res_price)
        for i in range(0,len(res_price)):
            res_p = res_p + res_price[i] + ' '
        
        if len(res_p) <= 3 and len(res_p) > 0:
            res_p = res_p + '000'
        if len(res_p) > 0:
            res_p = res_p + '₽'
        res_p = re.sub(r'\s+', '', res_p)

        cursor.execute('INSERT INTO database (user_id, text, date, sharp, price) VALUES (?, ?, ?, ?, ?)', (user_id, text, date_1, hashtag, res_p))
        connection.commit()

client.run_until_disconnected()

