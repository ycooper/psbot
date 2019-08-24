from urllib.request import Request, urlopen, quote
import json
import time
import datetime
import random

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

f = open("access_token", "r")
access_token = f.read()
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

while True:
    response = urlopen(server + '?act=a_check&key=' + key + '&ts=' + ts + '&wait=' + wait)
    r = response.read()
    d = json.loads(str(r, 'utf-8'))
    if 'updates' in d:
        for dcurrent in d['updates']:
            if dcurrent['type'] == 'message_new':
                print(r)

                uid = str(dcurrent['object']['from_id'])
                randuid = str(random.randint(0, 2147483647))
                user_response = urlopen(
                    'https://api.vk.com/method/users.get?user_ids=' + uid + '&access_token=' + access_token + '&v=' + api_version)
                ur = json.loads(str(user_response.read(), 'utf-8'))
                # print (ur)
                print('Message from: ' + ur['response'][0]['first_name'] + ' ' + ur['response'][0][
                    'last_name'] + ' ' + uid)
                print('Message: \"' + dcurrent['object']['text'] + '\"')
                if (dcurrent['object']['attachments']):
                    print('Attachments:')
                    for att in dcurrent['object']['attachments']:
                        print(att['type'])
                peer_id = dcurrent['object']['peer_id']
                print('Peer id: ' + str(peer_id))

                message = quote('Список доступных комманд:\n\n - \"Какая сейчас пара?\"\n - \"Процитируй что-нибудь\"')
                day_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

                current_class = ['пара', 'сейчас', 'сколько врем', 'который час']
                if any(substring in dcurrent['object']['text'].lower() for substring in current_class):
                    message = quote(day_of_week[datetime.datetime.today().weekday()]+'\n'+datetime.datetime.today().strftime("%Y-%m-%d %H.%M.%S"))

                citation = ['цитат', 'цити', 'процит', 'фразеологизм', 'афоризм', 'мотиви', 'мотивац']
                if (dcurrent['object']['attachments']) or ('geo' in dcurrent['object']) or any(substring in dcurrent['object']['text'].lower() for substring in citation):
                    message = quote(urlopen(Request('http://api.forismatic.com/api/1.0/?method=getQuote&format=text&lang=ru', headers={'User-Agent': 'Mozilla/5.0'})).read().decode("utf-8", "replace"))

                response = urlopen('https://api.vk.com/method/messages.send?user_id='+str(peer_id)+'&random_id='+randuid+'&message='+message+'&access_token='+access_token+'&v='+api_version)

                print()
    ts = d['ts']
    time.sleep(1)