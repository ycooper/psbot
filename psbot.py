#!/usr/bin/python3.5
from urllib.request import Request, urlopen, quote, unquote, urlretrieve
import urllib.parse
from os.path import dirname, abspath
from pytz import timezone
from pytz import all_timezones
import json
import time
import datetime
import random
import os

from docx_parser import get_schedule

print('''
 .S_sSSs      sSSs   .S_SSSs      sSSs_sSSs    sdSS_SSSSSSbs  
.SS~YS%%b    d%%SP  .SS~SSSSS    d%%SP~YS%%b   YSSS~S%SSSSSP  
S%S   `S%b  d%S'    S%S   SSSS  d%S'     `S%b       S%S       
S%S    S%S  S%|     S%S    S%S  S%S       S%S       S%S       
S%S    d*S  S&S     S%S SSSS%P  S&S       S&S       S&S       
S&S   .S*S  Y&Ss    S&S  SSSY   S&S       S&S       S&S       
S&S_sdSSS   `S&&S   S&S    S&S  S&S       S&S       S&S       
S&S~YSSY      `S*S  S&S    S&S  S&S       S&S       S&S       
S*S            l*S  S*S    S&S  S*b       d*S       S*S       
S*S           .S*P  S*S    S*S  S*S.     .S*S       S*S       
S*S         sSS*S   S*S SSSSP    SSSbs_sdSSS        S*S       
S*S         YSS'    S*S  SSY      YSSP~YSSY         S*S       
SP                  SP                              SP        
Y                   Y                               Y         

        \nBy 4cpr, 2019\n''')

file_path_separator = ['/']
schedule = []
global_schedule = [[{}]]
day_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
groups = []
user_settings = {}
user_filters = {}


def get_download_path(separator):
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        separator[0] = '\\'
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        separator[0] = '/'
        # return os.path.join(os.path.expanduser('~'), 'downloads')
        dir_name = '/tmp/psbot'
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        return dir_name


def creation_date(path_to_file):
    if os.name == 'nt':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            return stat.st_mtime


def parse_schedule(schedule):
    global global_schedule
    last_hour = 100  # It is actually time like 01:00 ('hhmm'-like numbers) in int
    # Counter to store hours as a list
    h_counter = 0
    day = 0
    # print("")
    global_schedule[0] = [{}]
    for hour in schedule:
        # print(hour)
        for key, value in hour.items():
            if key == '':
                """
                print("")
                print("Hours in file: {0}".format(str(value)[:-2]))
                print("Last hour: {0}".format(str(last_hour)[:-2]))
                print("Day: {0}".format(day))
                """
                if int(str(value)[:-2]) < int(str(last_hour)[:-2]):
                    day += 1
                    h_counter = 0
                    # print("NEW DAY #{0}".format(day))
                    global_schedule.append([{}])
                elif int(str(value)[:-2]) > int(str(last_hour)[:-2]):
                    # print("HOUR INCREASED")
                    h_counter += 1
                    global_schedule[day].append({})
                global_schedule[day][h_counter]['start_time'] = value
                # print("Writing start time: {0}".format(global_schedule[day][h_counter]))
                last_hour = value
            else:
                if key not in groups:
                    groups.append(key)
                global_schedule[day][h_counter][key] = value
                """
                print("{0} на паре: {1}".format(key, value))
                print("Hour counter: {0}".format(h_counter))
                print("Current day: {0}".format(global_schedule[day]))
                print("{0} days".format(len(global_schedule)))
                print("{0} hours".format(len(global_schedule[day])))
                print("Attempting to write global_schedule[{0}][{1}]".format(day, h_counter))
                print("")
        print("")
    print("global_schedule:")
    print(global_schedule)
    """


def get_current_pair(peer_id=0):
    # Some nasty time-magic
    # TODO autodetect correct Moscow time
    gerzone = timezone('Etc/GMT+6')
    loc_dt = gerzone.localize(datetime.datetime.today()).astimezone(timezone('Etc/GMT+3'))
    # print("local dt: {0}: ".format(loc_dt))
    loc_dt_now = gerzone.localize(datetime.datetime.now()).astimezone(timezone('Etc/GMT+3'))
    # print("local dt now: {0}: ".format(loc_dt_now))
    # day = datetime.datetime.today().astimezone(timezone('Europe/Moscow')).weekday()
    day = loc_dt.weekday()
    # class duration: 1 h 30 min
    delta = datetime.timedelta(0, 0, 0, 0, 30, 1)
    class_current_flag = False
    s_message = day_of_week[loc_dt.weekday()] + '\n' + \
                loc_dt.strftime(
                    "%Y-%m-%d %H.%M.%S")
    if not day < len(global_schedule):
        s_message = s_message + "\nВыходной день, пар нет"
    else:
        for hour in global_schedule[day]:
            class_hour = int(str(hour['start_time'])[:-2])
            class_minute = int(str(hour['start_time'])[-2:])
            class_start = datetime.time(class_hour, class_minute)
            current_delta = loc_dt_now.replace(tzinfo=None) - datetime.datetime.combine(loc_dt.replace(tzinfo=None),
                                                                                        class_start)
            if current_delta < delta and current_delta > -delta:
                td1 = datetime.timedelta(0, 0, 0, 0, class_minute, class_hour)
                beginning = ':'.join(str(td1).split(':')[:2])
                td2 = datetime.timedelta(0, 0, 0, 0, class_minute + 30, class_hour + 1)
                ending = ':'.join(str(td2).split(':')[:2])
                if current_delta >= datetime.timedelta(0):
                    s_message = s_message + "\nТекущая пара ({0} - {1}):".format(beginning, ending)
                else:
                    if -current_delta < delta:
                        s_message = s_message + "\nСледующая пара ({0} - {1}):".format(beginning, ending)
                for k, v in hour.items():
                    if k != 'start_time':
                        if k in user_filters[peer_id] or peer_id == 0 or peer_id not in user_filters:
                            s_message = s_message + "\n{0}: {1}".format(k, v)
                            print("s_message: \n{0}".format(s_message))
                            class_current_flag = True
        if not class_current_flag:
            s_message = s_message + "\nУчебный день окончен"

    return quote(s_message)


# Connecting to Long Poll server
try:
    f = open(dirname(abspath(__file__)) + "/access_token", "r")
except IOError:
    print('Error: File does not appear to exist.')
f = open(dirname(abspath(__file__)) + "/access_token", "r")
# 0a byte is eof
access_token = f.read().rstrip('\x0a')
f.close()
api_version = '5.101'
group_id = '183091952'
random.seed()
response = urlopen(
    'https://api.vk.com/method/groups.getLongPollServer?group_id=' + group_id + '&access_token=' + access_token + '&v=' + api_version)
d = json.loads(str(response.read(), 'utf-8'))
# print(d)
print('key: ' + d['response']['key'])
key = d['response']['key']
print('server: ' + d['response']['server'])
server = d['response']['server']
print('ts: ' + d['response']['ts'] + '\n')
ts = d['response']['ts']
wait = '25'

# Searcing vk for schedule in group
q = quote("расписание")
doc_type = str(1)
count = str(1000)
download_path = get_download_path(file_path_separator)
user_response = urlopen(
    'https://api.vk.com/method/docs.search?q=' + q + '&access_token=' + access_token + '&v=' + api_version + "&search_own&count=" + count)
ur = json.loads(str(user_response.read(), 'utf-8'))
print(ur)

# Filtering search results
print("Searching schedule files (.docx) in {0} results...".format(len(ur['response']['items'])))
f_counter = 0
fd_counter = 0
print("My group id: {0}".format(group_id))
for item in ur['response']['items']:
    # if item['owner_id'] < 0:
    # print("Group doc id: {0}".format(item['owner_id']))
    if item['owner_id'] == -int(group_id):
        print("Title: {0}".format(item['title']))
        value = datetime.datetime.fromtimestamp(item['date'])
        print("Upload time: {0}".format(value))
        print("Size: {0:.2f} KB".format(item['size'] * pow(2, -10)))
        print("url: {0}".format(item['url']))
        print()
        f_counter += 1
        file_path = download_path + file_path_separator[0] + item['title']
        print(file_path)
        print("Remote file date: {0}".format(datetime.datetime.fromtimestamp(item['date'])))

        # Downloading schedule file
        if os.path.isfile(file_path):
            print("Local file date: {0}".format(datetime.datetime.fromtimestamp(int(creation_date(file_path)))))
            if item['date'] > int(creation_date(file_path)):
                urlretrieve(item['url'], file_path)
                fd_counter += 1
        else:
            urlretrieve(item['url'], file_path)
            fd_counter += 1
        schedule = get_schedule(file_path)
        print('Parsing...')
        parse_schedule(schedule)

user_filters[0] = groups
print()
print("{0} schedule files found".format(f_counter))
print("{0} files were downloaded".format(fd_counter))
print("Saving files to: {0}".format(download_path))
get_current_pair()
print("Parsed schedule for groups: \n{0}".format(groups))

empty_keyboard = {
    'one_time': True,
    'buttons': [[{}]]
}
keyboard = empty_keyboard.copy()
keyboard['one_time'] = False
g_counter = 0
row_counter = 0
keyboard['buttons'][0].pop()
for group in groups:
    if g_counter == 4:
        keyboard['buttons'].append([])
        row_counter += 1
        g_counter = 0
    keyboard['buttons'][row_counter].append({
        'action': {
            'type': 'text',
            "payload": "{\"button\": \"" + group + "\"}",
            'label': group
        },
        'color': 'secondary'
    })
    g_counter += 1

while True:
    response = urlopen(server + '?act=a_check&key=' + key + '&ts=' + ts + '&wait=' + wait)
    r = response.read()
    d = json.loads(str(r, 'utf-8'))
    settings_flag = False
    if 'updates' in d:
        for d_current in d['updates']:
            if d_current['type'] == "message_new":
                print(r)
                message = quote(
                    'Список доступных комманд:\n\n - \"Какая сейчас пара?\"\n - "Настройки"\n - \"Процитируй что-нибудь\"')
                peer_id = d_current['object']['peer_id']
                print('Peer id: ' + str(peer_id))

                # Checking user keyboard settings
                if peer_id not in user_settings:
                    user_settings[peer_id] = keyboard
                    user_filters[peer_id] = []
                # Updating keyboard settings from keyboard event
                if 'payload' in d_current['object']:
                    settings_flag = True
                    print("PAYLOAD received: {0}".format(d_current['object']['payload']))
                    if 'command' in json.loads(d_current['object']['payload']):
                        message = "Выберите группы для отображения расписания"
                        break
                    print("FUCKING SHIiiittt: {0}".format(user_settings[peer_id]))
                    user_settings_copy = user_settings.copy()
                    for row in user_settings[peer_id]['buttons']:
                        for button in row:
                            l_group = json.loads(button['action']['payload'])['button']
                            r_group = json.loads(d_current['object']['payload'])['button']
                            if l_group == r_group:
                                print("PEEEEEEEEERRRRR: {0}".format(peer_id))
                                if button['color'] != 'primary':
                                    print("Peer id: {0}; Button color: {1}".format(peer_id, button['color']))
                                    print(user_settings)
                                    button['color'] = 'primary'
                                    print("Peer id: {0}; Button color: {1}".format(peer_id, button['color']))
                                    print(user_settings)
                                    message = quote("Включено отображение расписания группы {0}".format(l_group))
                                    user_filters[peer_id].append(l_group)
                                else:
                                    print("Peer id: {0}; Button color: {1}".format(peer_id, button['color']))
                                    print(user_settings)
                                    button['color'] = 'secondary'
                                    print("Peer id: {0}; Button color: {1}".format(peer_id, button['color']))
                                    print(user_settings)
                                    message = quote("Отключено отображение расписания группы {0}".format(r_group))
                                    if l_group in user_filters[peer_id]:
                                        user_filters[peer_id].remove(l_group)
                print("USER FILTERS: {0}".format(user_filters))

                uid = str(d_current['object']['from_id'])
                randuid = str(random.randint(0, 2147483647))
                user_response = urlopen(
                    'https://api.vk.com/method/users.get?user_ids=' + uid + '&access_token=' + access_token + '&v='
                    + api_version)
                ur = json.loads(str(user_response.read(), 'utf-8'))
                # print (ur)
                print('Message from: ' + ur['response'][0]['first_name'] + ' ' + ur['response'][0][
                    'last_name'] + ' ' + uid)
                print('Message: \"' + d_current['object']['text'] + '\"')
                if d_current['object']['attachments']:
                    print('Attachments:')
                    for att in d_current['object']['attachments']:
                        print(att['type'])

                current_class = ['пара', 'сейчас', 'сколько врем', 'который час']
                if any(substring in d_current['object']['text'].lower() for substring in current_class):
                    message = get_current_pair(peer_id)

                citation = ['цитат', 'цити', 'процит', 'фразеологизм', 'афоризм', 'мотиви', 'мотивац']
                if (d_current['object']['attachments']) or ('geo' in d_current['object']) or any(
                        substring in d_current['object']['text'].lower() for substring in citation):
                    assert isinstance(urlopen(
                        Request('http://api.forismatic.com/api/1.0/?method=getQuote&format=text&lang=ru',
                                headers={'User-Agent': 'Mozilla/5.0'})).read, object)
                    message = quote(urlopen(
                        Request('http://api.forismatic.com/api/1.0/?method=getQuote&format=text&lang=ru',
                                headers={'User-Agent': 'Mozilla/5.0'})).read().decode("utf-8", "replace"))

                options = ['настройки', 'опции', 'options', 'settings']
                if any(substring in d_current['object']['text'].lower() for substring in options):
                    settings_flag = True
                    message = "Выберите группы для отображения расписания"

                print("Message to user:\n{0}".format(unquote(message)))
                url = "https://api.vk.com/method/messages.send"

                post_request_params = {
                    'peer_id': str(peer_id),
                    'random_id': randuid,
                    'message': unquote(message),
                    'access_token': access_token,
                    'v': api_version
                }
                if settings_flag:
                    print("SENDING SETTINGS:\nPeer id: {0}\n{1}".format(peer_id, user_settings[peer_id]))
                    post_request_params['keyboard'] = json.dumps(user_settings[peer_id].copy())
                    print("Global user settings:\n{0}".format(user_settings))
                query_string = urllib.parse.urlencode(post_request_params)
                data = query_string.encode("ascii")

                response = urlopen(url, data)
                print(response.read())
                print()
    ts = d['ts']
    time.sleep(1)
