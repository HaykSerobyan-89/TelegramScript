import os
import time
from telethon import TelegramClient
from functions import scraper, send_message

clients = []

with open('accounts.txt', 'r') as f:
    for line in f.readlines():
        phone, api_id, api_hash = line.split(',')
        api_id = int(api_id)
        if api_hash.endswith('\n'):
            api_hash = api_hash[:-1]
        try:
            client = TelegramClient(phone, api_id, api_hash)
            clients.append(client)
        except Exception as err:
            print(err)
            continue

try:
    for client in clients:
        with client:
            client.start()
            # client.loop.run_until_complete(send_message(client))

    with clients[0]:
        client.loop.run_until_complete(scraper(clients[0]))

    time.sleep(10)
    for client in clients:
        with client:
            client.loop.run_until_complete(send_message(client))
            client.disconnect()
except KeyboardInterrupt as err:
    print('\n!!! THE PROGRAM STOPPED BY USER !!!')
    print('     ALL SESSIONS ARE DELETED')
    for file in os.listdir():
        if file.endswith('.session'):
            os.remove(file)
