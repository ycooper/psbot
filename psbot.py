#!/usr/bin/python3.5
from urllib.request import Request, urlopen, quote, urlretrieve
from os.path import dirname, abspath
from datetime import datetime
import http
import html
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


def get_download_path(separator):
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        separator[0] = '\\'
        print(file_path_separator)
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        separator[0] = '/'
        print(file_path_separator)
        #return os.path.join(os.path.expanduser('~'), 'downloads')
        os.mkdir('/tmp/psbot')
        return '/tmp/psbot'


f = open(dirname(abspath(__file__)) + "/access_token", "r")
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

q = quote("расписание")
doc_type = str(1)
count = str(1000)
download_path = get_download_path(file_path_separator)
user_response = urlopen(
    'https://api.vk.com/method/docs.search?q=' + q + '&access_token=' + access_token + '&v=' + api_version + "&search_own&count=" + count)
ur = json.loads(str(user_response.read(), 'utf-8'))
# print(ur)
print("Searching schedule files (.docx) in {0} results...".format(len(ur['response']['items'])))
f_counter = 0
for item in ur['response']['items']:
    if item['owner_id'] == -int(group_id):
        print("Title: {0}".format(item['title']))
        value = datetime.datetime.fromtimestamp(item['date'])
        print("Upload time: {0}".format(value))
        print("Size: {0:.2f} KB".format(item['size'] * pow(2, -10)))
        print("url: {0}".format(item['url']))
        print()
        f_counter += 1
        print("Separator: {0}".format(file_path_separator))
        file_path = download_path + file_path_separator[0] + item['title']
        print(file_path)
        urlretrieve(item['url'], file_path)
print("{0} schedule files found".format(f_counter))
print("Saving files to: {0}".format(download_path))

while True:
    response = urlopen(server + '?act=a_check&key=' + key + '&ts=' + ts + '&wait=' + wait)
    r = response.read()
    d = json.loads(str(r, 'utf-8'))
    if 'updates' in d:
        for d_current in d['updates']:
            if d_current['type'] == "message_new":
                print(r)

                uid = str(d_current['object']['from_id'])
                randuid = str(random.randint(0, 2147483647))
                user_response = urlopen(
                    'https://api.vk.com/method/users.get?user_ids=' + uid + '&access_token=' + access_token + '&v=' + api_version)
                ur = json.loads(str(user_response.read(), 'utf-8'))
                # print (ur)
                print('Message from: ' + ur['response'][0]['first_name'] + ' ' + ur['response'][0][
                    'last_name'] + ' ' + uid)
                print('Message: \"' + d_current['object']['text'] + '\"')
                if d_current['object']['attachments']:
                    print('Attachments:')
                    for att in d_current['object']['attachments']:
                        print(att['type'])
                peer_id = d_current['object']['peer_id']
                print('Peer id: ' + str(peer_id))

                message = quote('Список доступных комманд:\n\n - \"Какая сейчас пара?\"\n - \"Процитируй что-нибудь\"')
                day_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

                current_class = ['пара', 'сейчас', 'сколько врем', 'который час']
                if any(substring in d_current['object']['text'].lower() for substring in current_class):
                    message = quote(
                        day_of_week[datetime.datetime.today().weekday()] + '\n' + datetime.datetime.today().strftime(
                            "%Y-%m-%d %H.%M.%S"))

                citation = ['цитат', 'цити', 'процит', 'фразеологизм', 'афоризм', 'мотиви', 'мотивац']
                if (d_current['object']['attachments']) or ('geo' in d_current['object']) or any(
                        substring in d_current['object']['text'].lower() for substring in citation):
                    assert isinstance(urlopen(
                        Request('http://api.forismatic.com/api/1.0/?method=getQuote&format=text&lang=ru',
                                headers={'User-Agent': 'Mozilla/5.0'})).read, object)
                    message = quote(urlopen(
                        Request('http://api.forismatic.com/api/1.0/?method=getQuote&format=text&lang=ru',
                                headers={'User-Agent': 'Mozilla/5.0'})).read().decode("utf-8", "replace"))

                response = urlopen('https://api.vk.com/method/messages.send?peer_id=' + str(
                    peer_id) + '&random_id=' + randuid + '&message=' + message + '&access_token=' + access_token + '&v=' + api_version)

                print()
    ts = d['ts']
    time.sleep(1)
