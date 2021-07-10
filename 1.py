import tkinter as tk
import sqlite3
import re
import datetime

from tkinter import ttk
from telethon import TelegramClient, events
from telethon.sync import TelegramClient
from telethon.tl.types import MessageFwdHeader
from telethon.tl.types.messages import ChatsSlice

from  data import api_id, api_hash, api_client, channels

class DB:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.c.execute("""CREATE TABLE IF NOT EXISTS database(
            user_id INTEGER,
            text TEXT,
            date DATE,
            price TEXT,
            URL TEXT,
            sharp TEXT);
            """)
        self.conn.commit()

    def insert_data(self, user_id, text, date_1, hashtag, res_p):
        self.c.execute('INSERT INTO database (user_id, text, date, sharp, price) VALUES (?, ?, ?, ?, ?)', (user_id, text, date_1, hashtag, res_p))
        self.conn.commit()

    def delete_data(self):
        self.c.execute('DELETE FROM database')
        self.conn.commit()

db = DB()

date = datetime.datetime.today()
last_date = date - datetime.timedelta(days = 180)

client = TelegramClient('Me', api_id, api_hash)
client.start()

@client.on(events.NewMessage)
async def event_handler(event):

    if event.chat.username in channels:
       chat = await event.get_input_chat()
       msg = await client.get_messages(chat.channel_id, limit = 1) 
       await client.forward_messages(api_client, msg) 
    
    db.delete_data()

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

        db.insert_data(user_id, text, date_1, hashtag, res_p)

client.run_until_disconnected()

