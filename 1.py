import sqlite3
import re
import datetime
import tkinter as tk

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
            ID INTEGER,
            text_msg TEXT,
            date DATE,
            price TEXT,
            hash TEXT);
            """)
        self.conn.commit()

    def insert_data(self, user_id, text_msg, date_1, hashtag, res_p):
        self.c.execute('INSERT INTO database (ID, text_msg, date, hash, price) VALUES (?, ?, ?, ?, ?)', (user_id, text_msg, date_1, hashtag, res_p))
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
        text_msg = message.text
        user_id = message.id
        date_1 = message.date

        hashtag = str()
        text_str = str(text_msg)
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
            res_p = res_p + res_price[i]        
        if len(res_p) <= 3 and len(res_p) > 0:
            res_p = res_p + '000'
        if len(res_p) > 0:
            res_p = res_p + '₽'
        res_p = re.sub(r'\s+', '', res_p)

        db.insert_data(user_id, text_msg, date_1, hashtag, res_p)


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.init_main()
        self.db = db
        self.view_records()

    def init_main(self):
        toolbar = tk.Frame(bg='#d7d8e0', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.search_img = tk.PhotoImage(file='search.gif')
        btn_search = tk.Button(toolbar, text='Поиск', bg='#d7d8e0', bd=0, image=self.search_img,
        compound=tk.TOP, command=self.open_search_dialog)
        btn_search.pack(side=tk.LEFT)

        self.refresh_img = tk.PhotoImage(file='refresh.gif')
        btn_refresh = tk.Button(toolbar, text='Обновить', bg='#d7d8e0', bd=0, image=self.refresh_img, compound=tk.TOP, 
        command= lambda:[client.start(), self.view_records()])
        btn_refresh.pack(side=tk.LEFT)

        self.tree = ttk.Treeview(self, columns=('ID', 'text_msg', 'date', 'price', 'hash'), height=15, show='headings')

        self.tree.column('ID', width=30, anchor=tk.CENTER)
        self.tree.column('text_msg', width=365, anchor=tk.CENTER)
        self.tree.column('date', width=150, anchor=tk.CENTER)
        self.tree.column('price', width=100, anchor=tk.CENTER)
        self.tree.column('hash', width=100, anchor=tk.CENTER)

        self.tree.heading('ID', text='ID')
        self.tree.heading('text_msg', text='Сообщение')
        self.tree.heading('date', text='Дата')
        self.tree.heading('price', text='Цена')
        self.tree.heading('hash', text='Хэсштэг')
        self.tree.pack()

    def records(self, user_id, text_msg, date_1, hashtag, res_p):
        self.db.insert_data(user_id, text_msg, date_1, hashtag, res_p)
        self.view_records()

    def view_records(self):
        self.db.c.execute('''SELECT * FROM database''')

        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.db.c.fetchall()]

    def search_records(self, text_msg, price, hash):
        text_msg = ('%' + text_msg + '%',)
        price = ('%' + price + '%',)
        hash = ('%' + hash + '%',)
        self.db.c.execute('''SELECT * FROM database WHERE text_msg LIKE ?''', text_msg)
        self.db.c.execute('''SELECT * FROM database WHERE hash LIKE ?''', hash)
        self.db.c.execute('''SELECT * FROM database WHERE price LIKE ?''', price)
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.db.c.fetchall()]

    def open_dialog(self):
        Child()

    def open_search_dialog(self):
        Search()


class Child(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_child()
        self.view = app

    def init_child(self):

        label_text_msg = tk.Label(self, text='Сообщение:')
        label_text_msg.place(x=50, y=50)
        label_date = tk.Label(self, text='Дата:')
        label_date.place(x=50, y=80)
        label_price = tk.Label(self, text='Цены:')
        label_price.place(x=50, y=110)
        label_hash = tk.Label(self, text='Хэштэг:')
        label_hash.place(x=50, y=140)

        self.entry_text_msg = ttk.Entry(self)
        self.entry_text_msg.place(x=200, y=50)

        self.entry_money = ttk.Entry(self)
        self.entry_money.place(x=200, y=110)


        self.grab_set()
        self.focus_set()


class Search(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.init_search()
        self.view = app

    def init_search(self):
        self.title('Поиск')
        self.geometry('300x100+400+300')
        self.resizable(False, False)

        label_search = tk.Label(self, text='Поиск')
        label_search.place(x=50, y=20)

        self.entry_search = ttk.Entry(self)
        self.entry_search.place(x=105, y=20, width=150)

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=185, y=50)

        btn_search = ttk.Button(self, text='Поиск')
        btn_search.place(x=105, y=50)
        btn_search.bind('<Button-1>', lambda event: self.view.search_records(self.entry_search.get()))
        btn_search.bind('<Button-1>', lambda event: self.destroy(), add='+')

if __name__ == "__main__":
    root = tk.Tk()
    db = DB()
    app = Main(root)
    app.pack()
    root.title("Household database")
    root.geometry("750x450+300+300")
    root.resizable(False, False)
    root.mainloop()

