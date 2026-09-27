import requests
import uuid
import time
import openpyxl
from openpyxl.styles import Font
from openpyxl import utils
import datetime


ACCESS_TOKEN = 'lC5vOv7JESFgpQvHOEJ5iiMZzT5gmAMsBaMdolmf'
SAX_GROUP_ID = '95694848'
SAX_ANCMNT_ID = '95830618'
FIRST_MSG_ID = '169223056136399015'
MY_USER_ID = '60129484'


# A dictionary where the keys are user_ids of members in the sax groupchat
# The values are a list with the first element being the nickname of member
# The second element is the number of times they have been spotted
# The third element is the number of people they have spotted
# The fourth element is the number of invalid spots they have
# The fifth element is the ratio (this is filled out at the very end)
sax_group_members = {}

number_of_spots = 0
invalid_spots = 0
"""
invalid_ids = ['169272373093077945', '169273511392726465',
               '169283108218156139', '169283111221014983',
               '169283231013212258', '169283236602289778',
               '169284171943577065', '169290835889954983',
               '169334850404730571', '169342150595710648',
               '169352158987686465', '169412473088917334',
               '169483982810482431', '169488739874509837',
               '169499155589019837', '169507668420860665',
               '169522971156730665']
"""
invalid_ids = ['169272373093077945', '169273511392726465',
               '169283108218156139', '169283111221014983',
               '169283231013212258', '169283236602289778',
               '169284171943577065', '169290835889954983',
               '169334850404730571', '169342150595710648',
               '169352158987686465', '169412473088917334',
               '169483982810482431', '169488739874509837',
               '169499155589019837', '169507668420860665',
               '169522971156730665', '169578094760500519',
               '169582280808995542', '169594093860278899',
               '169611805402825677', '169611826316890519',
               '169611992601350519', '169735501794385934']


def list_groups():
    """Prints out the list of groups the user is in.
    prints in the format of name, id. Does not return
    a value."""
    url = 'https://api.groupme.com/v3/groups'
    params = {'token': ACCESS_TOKEN}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        groups = response.json()['response']

        for group in groups:
            print(f"Group Name: {group['name']}, Group ID: {group['id']}")
    else:
        print("Error fetching groups:", response.status_code)


def get_most_recent_message(group_id=SAX_GROUP_ID):
    """Returns the most recent message from the given group_id"""
    url = f'https://api.groupme.com/v3/groups/{group_id}/messages'
    params = {'token': ACCESS_TOKEN, 'limit': 1}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        messages = response.json()['response']['messages']
        if messages:
            most_recent_message = messages[0]
            return most_recent_message
        else:
            return None
    else:
        print('Error fetching messages: ', response.status_code)
        return None


def send_message(message_text):
    """Sends a message to the Sax groupchat. Uses message_text
    as the text to send with the message. Uses uuid to generate
    a random source_guid to use with the message."""
    url = f'https://api.groupme.com/v3/groups/{SAX_GROUP_ID}/messages'
    headers = {'Content-Type': 'application/json'}
    data = {
        'message': {
            'source_guid': str(uuid.uuid4()),
            'text': message_text
        }
    }
    params = {'token': ACCESS_TOKEN}

    response = requests.post(url, headers=headers, json=data, params=params)

    if response.status_code == 201:
        print('Message send successfully!')
    else:
        print('Error sending message: ', response.status_code)


def count_group_message():
    """Returns the number of messages sent in the sax group"""
    url = f'https://api.groupme.com/v3/groups/{SAX_GROUP_ID}/messages'
    params = {'token': ACCESS_TOKEN}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()['response']['count']
    else:
        print('Error fetching the group messages:', response.status_code)
        return None


def get_members():
    """Updates sax_groups_members with all the members in the sax gc.
    sax_group_members is a dictionary where the keys are the members'
    user_ids and the value is a list where the first element is the
    member's nickname"""
    url = f'https://api.groupme.com/v3/groups/{SAX_GROUP_ID}'
    params = {'token': ACCESS_TOKEN}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        members = response.json()['response']['members']
        if members:
            for member in members:
                sax_group_members[member['user_id']] = \
                    [member['nickname'], 0, 0, 0, 0]
        else:
            print('no members found :(')
    else:
        print('Error fetching group details', response.status_code)


def get_messages_before(before_id, limit=100):
    """Returns the list of limit messages before the message with the id
    before_id. If there are no messages before before_id then prints out
    before_id saying that this is the earliest message."""
    url = f'https://api.groupme.com/v3/groups/{SAX_GROUP_ID}/messages'
    params = {'token': ACCESS_TOKEN, 'limit': limit, 'before_id': before_id}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        messages = response.json()['response']['messages']
        if messages:
            return messages
        else:
            return None
    elif response.status_code == 304:
        print(f'{before_id} is the earliest message in this group')
        return None
    else:
        print(f'Error fetching messages before id, {before_id}: '
              f'{response.status_code}')
        return None


def get_messages_after(after_id, limit=1):
    """Returns the list of limit messages immediately following the
    message with the id after_id. If there are no messages after
    after_id, then prints out that there are no messages after after_id"""
    url = f'https://api.groupme.com/v3/groups/{SAX_GROUP_ID}/messages'
    params = {'token': ACCESS_TOKEN, 'limit': limit, 'after_id': after_id}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        messages = response.json()['response']['messages']
        if messages:
            return messages
        else:
            return None
    elif response.status_code == 304:
        print(f'There are no messages after {after_id}')
        return None
    else:
        print(f'Error fetching messages after id, {after_id}: '
              f'{response.status_code}')
        return None


def get_message_id(message_id):
    """Returns the message with the id: message_id"""
    message = get_messages_after(message_id, 1)[0]
    message = get_messages_before(message['id'], 1)[0]
    return message


def get_most_liked_message():
    """Returns the message with the most likes."""
    most_recent = get_most_recent_message()
    if not most_recent:
        return None
    messages = get_messages_before(most_recent['id'])
    max_likes = len(most_recent['favorited_by'])
    most_liked = most_recent
    num_parsed = 1
    num_say_spotted = 0

    while messages:
        for message in messages:
            if message['text']:
                if 'spotted' in message['text'] or \
                        'Spotted' in message['text']:
                    num_say_spotted += 1
            num_likes = len(message['favorited_by'])
            if num_likes > max_likes:
                max_likes = num_likes
                most_liked = message
            num_parsed += 1
        messages = get_messages_before(message['id'])
    # print(f'Number of messages parsed: {num_parsed}')
    # print(f'Number of attempted spots: {num_say_spotted}')
    return most_liked


def print_most_liked_message():
    """Prints the most liked message out with the number of likes
    it received and lists out who all liked it."""
    most_liked_msg = get_most_liked_message()
    # print(most_liked_msg)
    print('Most liked message:')
    print(f"{most_liked_msg['name']}: {most_liked_msg['text']}")
    print('Liked by:')
    for user_id in most_liked_msg['favorited_by']:
        if user_id in sax_group_members.keys():
            print(f'\t{sax_group_members[user_id][0]}')
        else:
            print(f'\tid: {user_id} not in members')
    print(f"Number of likes: {len(most_liked_msg['favorited_by'])}")


def is_an_attempt(message):
    """Returns true if the message is counted as being an attempt to
    spot someone. Returns false otherwise."""
    if not message['text']:
        return False
    img_flag = False
    mention_flag = False
    text_flag = 'spotted' in message['text'] or 'Spotted' in message['text']
    for attachment in message['attachments']:
        if not img_flag:
            img_flag = attachment['type'] == 'image' or \
                       attachment['type'] == 'video'
        if not mention_flag:
            mention_flag = attachment['type'] == 'mentions'
    if text_flag and mention_flag and not img_flag:
        # print()
        # print(message)
        # print()
        prev_msg = get_messages_before(message['id'], 1)[0]
        for atch in prev_msg['attachments']:
            if atch['type'] == 'image':
                # print(f"image url: {atch['url']}")
                img_flag = True
    elif text_flag and mention_flag and img_flag:
        for atch in message['attachments']:
            if atch['type'] == 'image':
                # print(f"image url: {atch['url']}")
                break
    return img_flag and mention_flag and text_flag


def print_spot_msg(message):
    """prints out the image link then the message. prints out the 20
    messages immediately following message."""
    print(f"{message['name']}: {message['text']}")
    # print('Here are the next 20 messages')
    # following_messages = get_messages_after(message['id'], 20)
    # for msg in following_messages:
    #     print()
    #     for atch in msg['attachments']:
    #         if atch['type'] == 'reply':
    #             if atch['reply_id'] == message['id']:
    #                 print('This one has a reply to the message')
    #     # if msg['attachments']:
    #     #     print('This one has an attachment')
    #     print(f"{msg['name']}: {msg['text']}")


def is_valid_spot(message):
    """Gets user input on whether message is a valid spot or not and updates
    globals accordingly."""
    global number_of_spots
    global invalid_spots
    # TODO: get completely rid of user input
    #  (only say its invalid if its in the list)
    #  assume its valid until we find a message that replies
    #  to a spot saying its invalid then we properly update vals
    # print(f'in user in func message: {message}')

    # if message['id'] in invalid_ids:
    #     invalid_spots += 1
    #     sax_group_members[message['user_id']][3] += 1
    # else:
    #     number_of_spots += 1
    #     for atch in message['attachments']:
    #         if atch['type'] == 'mentions':
    #             for uid in atch['user_ids']:
    #                 sax_group_members[uid][1] += 1
    #     sax_group_members[message['user_id']][2] += 1

    # user_in = input('Was that a valid spot (y/n): ')
    user_in = 'y'
    if message['id'] in invalid_ids:
        user_in = 'n'
    if user_in == 'y':
        # print('You chose to accept it')
        people_spotted = 0
        for atch in message['attachments']:
            if atch['type'] == 'mentions':
                for uid in atch['user_ids']:
                    if uid not in sax_group_members.keys():
                        sax_group_members[uid] = ['not here', 0, 0, 0, 0]
                    sax_group_members[uid][1] += 1
                    people_spotted += 1
                    # print(sax_group_members[uid])
        sax_group_members[message['user_id']][2] += people_spotted
        number_of_spots += people_spotted
    else:
        # print('You chose to deny it')
        invalid_spots += 1
        invalid_ids.append(message['id'])
        sax_group_members[message['user_id']][3] += 1
    # print(sax_group_members[message['user_id']])


def is_invalid_message(message):
    """If message replies to a valid spot and says invalid changes the stats
    to account for that spot being invalid"""
    global number_of_spots
    global invalid_spots
    for atch in message['attachments']:
        if atch['type'] == 'reply':
            if message['text'] and not ('invalid' in message['text'] or
                                        'Invalid' in message['text']):
                return
            invalid_spot = get_message_id(atch['reply_id'])
            if invalid_spot['id'] not in invalid_ids and \
                    is_an_attempt(invalid_spot):
                print('invalidating a spot!')
                # invalid_spot = get_message_id(atch['reply_id'])
                num_people = 0
                for msg_atch in invalid_spot['attachments']:
                    if msg_atch['type'] == 'mentions':
                        for uid in msg_atch['user_ids']:
                            # print(sax_group_members[uid][1])
                            sax_group_members[uid][1] -= 1
                            # print(sax_group_members[uid][1])
                            num_people += 1
                            # print(sax_group_members[uid])
                sax_group_members[invalid_spot['user_id']][2] -= num_people
                number_of_spots -= num_people
                sax_group_members[invalid_spot['user_id']][3] += 1
                invalid_spots += 1
                invalid_ids.append(invalid_spot['id'])
                # print(sax_group_members[invalid_spot['user_id']])
                # print()
            elif invalid_spot['id'] in invalid_ids:
                print('nice try!')


def process_spots():
    """Indexes through all the messages starting from the very first one.
    If a message has at least one image and one mention in the attachments
    and the word spotted in the text, prints the link to the image and
    the message. Then it prints out the next 20 messages following the
    message in question and asks the user for input determining whether the
    spot is valid or not. If it is valid then increments the third element
    of the sender's list and increments the second element of anyone who was
    mentioned. If the spot is invalid, adds the message_id to a list of invalid
    spots (so we can eliminate user input later). Also increments the fourth
    element of the sender's list. Also keeps track of the total number of
    attempted spots, totals number of successful spots, and total number of
    invalid spots."""
    global invalid_spots
    global number_of_spots
    messages = get_messages_after(FIRST_MSG_ID, 100)
    while messages:
        for message in messages:
            msg_id = message['id']
            # print(sax_group_members.keys())
            # print(message['user_id'])
            if message['user_id'] in sax_group_members.keys():
                if msg_id in invalid_ids:
                    invalid_spots += 1
                    sax_group_members[message['user_id']][3] += 1
                elif is_an_attempt(message):
                    # if msg_id < invalid_ids[-1]:
                    #     number_of_spots += 1
                    #     for atch in message['attachments']:
                    #         if atch['type'] == 'mentions':
                    #             for uid in atch['user_ids']:
                    #                 sax_group_members[uid][1] += 1
                    # else:
                    # print_spot_msg(message)
                    is_valid_spot(message)
                    # print('\n*****CURRENT STATS*****')
                    # print(f'number of spots: {number_of_spots}')
                    # print(f'number of invalid spots: {invalid_spots}')
                    # print(f'total number of attempts: '
                    #       f'{number_of_spots + invalid_spots}')
                    # print(f'invalid_ids: {invalid_ids}')
                    # print()
                else:
                    is_invalid_message(message)
                    # print('\n*****CURRENT STATS*****')
                    # print(f'number of spots: {number_of_spots}')
                    # print(f'number of invalid spots: {invalid_spots}')
                    # print(f'total number of attempts: '
                    #       f'{number_of_spots + invalid_spots}')
                    # print(f'invalid_ids: {invalid_ids}')
                    # print()

        time.sleep(.5)
        messages = get_messages_after(message['id'], 100)


def make_ratios():
    """
    Traverses through sax_group_members and sets the fifth element of the list
    in value to be the spot ratio of the member. The ratio is the number of
    people spotted divided by the times they have been spotted. If they have
    been spotted zero times, the ratio is just the number of people they have
    spotted.
    :return: nothing
    """
    for mem in sax_group_members:
        val = sax_group_members[mem]
        if val[1] == 0:
            val[4] = val[2]
        else:
            val[4] = round(val[2]/float(val[1]), 2)


def add_results_to_sheet():
    """Adds the results from processing the spots to the file
    'Sax 23-24 spotting results'"""
    wb = openpyxl.load_workbook('Sax 23-24 spotting results.xlsx')
    ws = wb.worksheets[0]
    header = ['Name', 'Spotting Ratio', 'People Spotted', 'Times Spotted', 'Invalid Spots']

    sheet = [header]
    for uid in sax_group_members:
        mem = sax_group_members[uid]
        row = [mem[0], mem[4], mem[2], mem[1], mem[3]]
        sheet.append(row)

    for row_index, row_data in enumerate(sheet, start=1):
        for col_index, cell_value in enumerate(row_data, start=1):
            ws.cell(row=row_index, column=col_index, value=cell_value)

    ft = Font(bold=True)
    for row in ws["A1:D1"]:
        for cell in row:
            cell.font = ft

    for column_index in range(1, ws.max_column + 1):
        max_length = 0
        column_letter = openpyxl.utils.get_column_letter(column_index)
        for cell in ws[column_letter]:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except TypeError:
                pass
        adjusted_width = max_length + 2
        ws.column_dimensions[column_letter].width = adjusted_width

    ws['A60'] = '# of spots'
    ws['B60'] = number_of_spots
    ws['A61'] = datetime.datetime.now().strftime('%m/%d/%Y %I:%M')

    wb.save('Sax 23-24 spotting results.xlsx')


if __name__ == "__main__":
    get_members()

    count = count_group_message()
    print(count)

    process_spots()

    make_ratios()

    name_width = 28
    print('*****SPOT RESULTS*****')
    print(f'name, times been spotted, # people spotted, # invalid spots, ratio')
    for mem_id in sax_group_members:
        member = sax_group_members[mem_id]
        print(f'{member[0]:{name_width}}{member[1]}\t{member[2]}  {member[3]}  {member[4]}')
    print(f'{invalid_spots} invalid spots, {number_of_spots + invalid_spots} '
          f'attempted spots')
    print(f'Total number of spots: {number_of_spots}')
    print(f'\ninvalid_ids = {invalid_ids}\n')

    print('*****RESULTS FROM LIST*****')
    list_spot_num = 0
    list_spotted_num = 0
    for mem_id in sax_group_members:
        member = sax_group_members[mem_id]
        list_spot_num += member[2]
        list_spotted_num += member[1]
    print(f'number of people spotted: {list_spotted_num}')
    print(f'number of spots: {list_spot_num}')

    add_results_to_sheet()
    """
    most_liked = get_most_liked_message()

    print(f"{most_liked['name']}: {most_liked['text']}")
    if most_liked['attachments']:
        print(most_liked['attachments'])
    """
