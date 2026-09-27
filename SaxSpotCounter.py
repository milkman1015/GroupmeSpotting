import requests
import uuid
import time
import openpyxl
from openpyxl.styles import Font
from openpyxl import utils
import datetime

ACCESS_TOKEN = ''
SAX_GROUP_ID = '95694848'
SAX_GROUP_ID_25 = '102585719'
SAX_ANCMNT_ID = '95830618'
FIRST_MSG_ID = '169223056136399015'
MY_USER_ID = '60129484'
FIRST_MSG_ID25 = '172429310710651409'

# A Dictionary for the list of members with the values we are measuring
# the keys are the Unique UIDs of the members
# The value is a list with several elements
# The first element is the user's nickname
# The second element is the number of spots they have
# The third element is the number of times they have been spotted
sax_group_members = {}

# Storing the last message checked to store in the file
last_messageid = '0'

# The number of spots that have happened
number_of_spots = 0
# Number of invalid spots
invalid_spots = 0


def get_first_message_id():
    """Returns the message id of the first message"""
    num_messages = int(count_group_message(SAX_GROUP_ID_25))
    print(num_messages)
    num_messages = int((num_messages / 100) + 1)
    print(num_messages)
    message_id = get_most_recent_message(SAX_GROUP_ID_25)['id']
    message = {}

    for i in range(0, num_messages):
        message = get_messages_before(message_id, 100, SAX_GROUP_ID_25)
        message = message[-1]
        message_id = message['id']
        print(i)
    print(message)


def get_most_recent_message(group_id=SAX_GROUP_ID_25):
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


def count_group_message(guid=SAX_GROUP_ID):
    """Returns the number of messages sent in the sax group"""
    url = f'https://api.groupme.com/v3/groups/{guid}/messages'
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
    url = f'https://api.groupme.com/v3/groups/{SAX_GROUP_ID_25}'
    params = {'token': ACCESS_TOKEN}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        members = response.json()['response']['members']
        if members:
            for member in members:
                sax_group_members[member['user_id']] = \
                    [member['nickname'], 0, 0]
            print(sax_group_members)
        else:
            print('no members found :(')
    else:
        print('Error fetching group details', response.status_code)


def get_messages_before(before_id, limit=100, group_id=SAX_GROUP_ID):
    """Returns the list of limit messages before the message with the id
    before_id. If there are no messages before before_id then prints out
    before_id saying that this is the earliest message."""
    url = f'https://api.groupme.com/v3/groups/{group_id}/messages'
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
    elif response.status_code == 429:
        print(f'got status 429 (in before), gonna try waiting for a little bit and then try again')
        time.sleep(5)
        return get_messages_before(before_id, limit, group_id)
    else:
        print(f'Error fetching messages before id, {before_id}: '
              f'{response.status_code}')
        print(f'here is the whole response:\n{response.json()}')
        return None


def get_messages_after(after_id, limit=1, group_id=SAX_GROUP_ID):
    """Returns the list of limit messages immediately following the
    message with the id after_id. If there are no messages after
    after_id, then prints out that there are no messages after after_id"""
    url = f'https://api.groupme.com/v3/groups/{group_id}/messages'
    params = {'token': ACCESS_TOKEN, 'limit': limit, 'after_id': after_id}
    response = requests.get(url, params=params)

    time.sleep(2) # try not to throttle api service

    if response.status_code == 200:
        messages = response.json()['response']['messages']
        if messages:
            return messages
        else:
            return None
    elif response.status_code == 304:
        print(f'There are no messages after {after_id}')
        return None
    elif response.status_code == 429:
        print(f'got status 429 (in after), gonna try waiting for a little bit and then try again')
        time.sleep(5)
        return get_messages_after(after_id, limit, group_id)
    elif response.status_code == 420:
        print('Too many requests, here is the message:')
        print(response)
        return None
    else:
        print(f'Error fetching messages after id, {after_id}: '
              f'{response.status_code}')
        return None


def get_message_id(message_id, guid=SAX_GROUP_ID):
    """Returns the message with the id: message_id"""
    # print(f'get message id id: {message_id}')
    message = get_messages_after(message_id, 1, guid)[0]
    # print(f'message after wanted id')
    message = get_messages_before(message['id'], 1, guid)[0]
    return message


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
    return


def count_likes(start_id=FIRST_MSG_ID25):
    """Sums up the total likes that each user received on their messages"""
    global last_messageid
    start_msg = get_message_id(start_id, SAX_GROUP_ID_25)
    # start_msg = get_most_recent_message(SAX_GROUP_ID_25)
    messages = get_messages_after(start_msg['id'], 100, SAX_GROUP_ID_25)
    while start_msg:
        for m in messages:
            if m['user_id'] in sax_group_members.keys():
                sax_group_members[m['user_id']][1] += len(m['favorited_by'])
                sax_group_members[m['user_id']][2] += 1

        last_messageid = messages[-1]['id']
        # print(messages[-1])
        messages = get_messages_after(messages[-1]['id'], 100, SAX_GROUP_ID_25)

        if not messages:
            break
    return


def is_an_attempt(message):
    """Returns true if the message is counted as being an attempt to spot
    someone. Returns false otherwise. A message is an attempted spot if the
    text contains spotted, it mentions one or more people, and it has an image
    or video attachment."""
    # If there isnt any text then it is obviously not an attempt
    if not message['text']:
        return False
    # Set up flags for the checks we need to do
    img_flag = False
    mention_flag = False
    text = message['text'].lower()
    text_flag = 'spotted' in text

    for attachment in message['attachments']:
        if not img_flag:
            img_flag = attachment['type'] == 'image' or \
                       attachment['type'] == 'video'
        if not mention_flag:
            mention_flag = attachment['type'] == 'mentions'
    # In the past I had to check if the image was in the message before but im
    # not doing that shit again.
    return img_flag and mention_flag and text_flag


def is_invalid(message):
    """Returns true if this message is invalidating a spot attempt. If true is
    returned then the invalidated message is also returned."""
    # message is an invalid message if it replies to a spot and contains
    # the test: "invalid"
    for atch in message['attachments']:
        if atch['type'] == 'reply':
            # print(f'is invalid message:\n{message}')
            if message['text'] and not ('invalid' in message['text'].lower()):
                return False, None
            invalid_spot = get_message_id(atch['reply_id'], SAX_GROUP_ID_25)
            if is_an_attempt(invalid_spot):
                return True, invalid_spot
            else:
                return False, None
    return False, None


def do_spot(message):
    """Updates the globals for the spot message.
    is_an_attempt(message) is expected to be true"""
    global number_of_spots

    # first check to make sure that the user_id is present in our list
    # should always be true but never hurts to check
    uid = message['user_id']
    if uid not in sax_group_members.keys():
        print(f'user id {uid} is not in the group')
        return

    # need to add the number of people spotted to the sender
    # first process spottees and count amount
    people_spotted = 0
    # now we need to scan the mentions for the people mentioned
    for atch in message['attachments']:
        if atch['type'] == 'mentions':
            for suid in atch['user_ids']:
                if suid == '-1':
                    print(f'before key error, message:\n{message}')
                    print('should not error')
                if suid in sax_group_members:
                    people_spotted += 1
                    sax_group_members[suid][2] += 1

    # have total number spotted so add it to spotters stats
    sax_group_members[uid][1] += people_spotted
    number_of_spots += people_spotted
    return


def invalidate_spot(invalid_spot):
    """updates sax_group_members according to invalid_spot
    invalid_spot is expected to be the message that is returned when is_invalid
    returns true"""
    global number_of_spots
    global invalid_spots

    # this function is essentially do_spot with very minor changes
    # do_spot should have already been run with this message as an input so
    # we can guarantee that the uid is in our list
    people_spotted = 0
    for atch in invalid_spot['attachments']:
        if atch['type'] == 'mentions':
            for suid in atch['user_ids']:
                people_spotted += 1
                sax_group_members[suid][2] -= 1

    sax_group_members[invalid_spot['user_id']][2] -= people_spotted
    number_of_spots -= people_spotted
    return


def process_messages():
    """Starts reading messages starting from either the first message or
    last_messageid. does all the checks for spots and stores the data and
    whatnot."""
    start_id = last_messageid if last_messageid != '0' else FIRST_MSG_ID25
    messages = get_messages_after(start_id, 100, SAX_GROUP_ID_25)
    while messages:
        next_start = ''
        for message in messages:
            if is_an_attempt(message):
                do_spot(message)
            invalid_flag, invalid_msg = is_invalid(message)
            if invalid_flag:
                invalidate_spot(invalid_msg)
            next_start = message['id']
        messages = get_messages_after(next_start, 100, SAX_GROUP_ID_25)
    return


def add_results_to_excel():
    """Adds the results of the calculation to an excel file"""
    wb = openpyxl.load_workbook('Sax Spotting Results 24-25.xlsx')
    ws = wb.worksheets[0]
    header = ['Name', 'Numbers of Spots', 'Times been Spotted', 'Ratio']

    sheet = [header]
    for uid in sax_group_members:
        mem = sax_group_members[uid]
        row = [mem[0], mem[1], mem[2], 0] if mem[2] == 0 else [mem[0], mem[1], mem[2], round(mem[1]/float(mem[2]), 2)]
        sheet.append(row)

    for row_index, row_data in enumerate(sheet, start=1):
        for col_index, cell_value in enumerate(row_data, start=1):
            ws.cell(row=row_index, column=col_index, value=cell_value)

    ft = Font(bold=True)
    for row in ws['A1:D1']:
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

    wb.save('Sax Spotting Results 24-25.xlsx')
    return


def store_data():
    """Stores data in a file to read from on next run"""
    wb = openpyxl.load_workbook('Sax Spotting Results 24-25.xlsx')
    ws = wb.worksheets[1]
    print("balls")
    # add all the member data
    sheet = [[len(sax_group_members.keys())]]
    for uid in sax_group_members:
        mem = sax_group_members[uid]
        row = [uid, mem[0], mem[1], mem[2]]
        sheet.append(row)

    # need to add the last messageid
    sheet.append([last_messageid])
    for x in sheet:
        print(x)

    for row_index, row_data in enumerate(sheet, start=1):
        for col_index, cell_value in enumerate(row_data, start=1):
            ws.cell(row=row_index, column=col_index, value=cell_value)

    wb.save('Sax Spotting Results 24-25.xlsx')
    return


def read_data():
    """Reads the data from the file to start where the last one ended"""
    global last_messageid
    wb = openpyxl.load_workbook('Sax Spotting Results 24-25.xlsx')
    ws = wb.worksheets[1]

    # Get all the rows from the sheet
    rows = list(ws.rows)
    # The first cell is the number of members to look for
    num_entries = int(rows[0][0].value)
    print(num_entries)

    # Loop over all the member entries
    for r in range(1, num_entries + 1):
        # Get the vals and keys for the dict
        val = [rows[r][1].value, int(rows[r][2].value), int(rows[r][3].value)]
        key = rows[r][0].value

        # put those into the dict
        sax_group_members[key] = val

    # assign the last_messageid so we know where to start from next
    last_messageid = rows[num_entries + 1][0].value
    return


def test():
    start = get_most_recent_message(SAX_GROUP_ID_25)
    msg = get_messages_before(start['id'], 100, SAX_GROUP_ID_25)
    for i in range(0, 2):
        print()
        for m in msg:
            # print(m)
            print(f'{m["name"]}: {m["text"]}')
        msg = get_messages_before(msg[-1]['id'], 100, SAX_GROUP_ID_25)
    print()
    for m in msg:
        print(f'{m["name"]}: {m["text"]}')
    print(msg[-1])
    return


def test2():
    msg = get_most_recent_message(SAX_GROUP_ID_25)
    msg = get_messages_after(msg['id'], 20, SAX_GROUP_ID_25)
    print(msg)
    if msg:
        print('L')
    return


def runner():
    """Calls all the functions in order to do the thing."""
    # Inits sax members
    # read_data()
    get_members()
    print(f'most recent message: {get_most_recent_message()}')
    # Does the data analyses
    # count_likes(last_messageid)
    # count_likes()
    process_messages()
    # Stores results for viewing
    add_results_to_excel()
    # Store the read stuff to start from later
    store_data()
    return


if __name__ == "__main__":
    gid = '88486800'
    runner()
    # read_data()
    # get_members()
    # print(sax_group_members)
    # print(get_most_recent_message(gid))
    # print(get_message_id(FIRST_MSG_ID25, SAX_GROUP_ID_25))
    # count_likes('172469226105465686')
    # test()
    # test2()
    # for pers in sax_group_members.keys():
    #     print(sax_group_members[pers])
    # count_likes(last_messageid)
    # for pers in sax_group_members.keys():
    #     print(sax_group_members[pers])
    # add_results_to_excel()
    # store_data()
