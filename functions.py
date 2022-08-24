import csv
import os
import time
from telethon.errors.rpcerrorlist import ChatAdminRequiredError
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, PeerChannel

all_participants = []

header = ['ID', 'NAME', 'SURNAME', 'USERNAME', 'PHONE', 'GROUP', 'MESSAGE']
message_sent = []
message_not_send = []

with open('received.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)


def get_groups_from_file(file="groups.txt") -> list:
    groups = []
    if os.path.exists(file):
        with open(file) as f:
            lines = f.readlines()
        groups = [el[:-1] if el.endswith('\n') else el for el in lines]
    else:
        print("Please add 'groups.txt' file with group names or ids in this directory . . .")
    return groups


def del_first_row():
    first_row = ''
    username = ''
    user = list()

    with open('all_users.txt', 'r', encoding='utf-8') as fin:
        data = fin.read().splitlines(True)
        first_row = data[0].strip('\n')
    with open('all_users.txt', 'w', encoding='utf-8') as fout:
        fout.writelines(data[1:])
    username = first_row.split('-')[-1]
    user.append(first_row.split('-')[1])
    if first_row.split('-')[2].isdigit():
        user.append(first_row.split('-')[3])
        user.append(first_row.split('-')[4])
        user.append(first_row.split('-')[5])
        user.append(first_row.split('-')[2])
        user.append(first_row.split('-')[0])
        user.append('Sent')
    else:
        user.append(first_row.split('-')[2])
        user.append(first_row.split('-')[3])
        user.append(first_row.split('-')[4])
        user.append(' ')
        user.append(first_row.split('-')[0])
        user.append('Sent')

    with open('received.csv', 'a+', encoding='utf-8') as f:
        # create the csv writer
        write = csv.writer(f)
        # write a row to the csv file
        write.writerow(user)
    return first_row, username


async def scraper(client):
    offset = 0
    limit = 100

    for group in get_groups_from_file():
        user_input_channel = group

        if user_input_channel.isdigit():
            entity = PeerChannel(int(user_input_channel))
        else:
            entity = user_input_channel
        try:
            my_channel = await client.get_entity(entity)
        except ValueError:
            print(f'{str(entity)}: Correct entity name or id')
            continue
        group_users = []
        while True:
            try:
                participants = await client(GetParticipantsRequest(
                    my_channel, ChannelParticipantsSearch(''), offset, limit,
                    hash=0
                ))
                print(f'Scraping from [ {my_channel.title}] group: {len(group_users)}')
                if not participants.users:
                    break
            except ChatAdminRequiredError:
                print(f'{my_channel.title}: This group is closed')
                break

            all_participants.extend(participants.users)
            group_users.extend(participants.users)
            offset += len(participants.users)

        for participant in all_participants:
            user_info = str(group) + '-' + str(participant.id) + '-'
            if participant.phone is not None:
                user_info += participant.phone + '-'
            if participant.first_name is not None:
                user_info += participant.first_name + '-'
            else:
                user_info += ' -'
            if participant.last_name is not None:
                user_info += participant.last_name + '-'
            else:
                user_info += ' -'
            if participant.username is not None:
                user_info += participant.username + '\n'
            else:
                continue
            with open(f'all_users.txt', 'a+', encoding='utf-8') as outfile:
                outfile.write(user_info)

    print(f"TOTAL USERS COUNT {len(all_participants)}")


async def send_message(client):
    me = await client.get_me()
    print(f'Start sending messages with {me.phone} account')
    # send message
    message = ''
    i = 1
    with open('message.txt', 'r', encoding='utf-8') as f:
        message += f.read()
        try:
            with open('all_users.txt', 'r', encoding='utf-8') as file:
                rows_count = len(file.readlines())
                file.close()

            for _ in range(rows_count - 1):

                user_info, username = del_first_row()

                user_entity = await client.get_entity(username)
                user_info = f'Id: ' + str(user_entity.id)
                if user_entity.first_name is not None:
                    user_info += f' Name: ' + user_entity.first_name
                if user_entity.last_name is not None:
                    user_info += f' Surname: ' + user_entity.last_name
                if user_entity.username is not None:
                    user_info += f' Username: ' + user_entity.username
                if user_entity.phone is not None:
                    user_info += f' Phone: ' + user_entity.phone

                # await client.send_message(user_entity, message, file='image.png')
                time.sleep(30)
                print(f"{i}. Sending to user --> ", user_info)
                i += 1
        except Exception as err:
            print(str(err))
            await client.disconnect()
            # delete session file after disconnecting
            # if os.path.exists(f'{me.phone}.session'):
            #     os.remove(f'{me.phone}.session')
