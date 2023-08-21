from datetime import datetime
try:
    from common import *
except Exception as e:
    from src.common import *
import json
import requests

# load config.json data
with open("config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)


class Bot:
    def __init__(self) -> None:
        self.slack_token = config['AUTH']['SLACK_OAUTH_TOKEN']
        self.slack_id = config['AUTH']['SLACK_ID']
        self.slack_channel_name = config['AUTH']['SLACK_CHANNEL_NAME']
        self.slack_webhook_chennel_url = config['AUTH']['SLACK_WEBHOOK_CHENNEL_URL']

    def sendMsg(self, blocks_data):
        try:
            header = {'Content-type': 'application/json'}
            # data = json.dumps({
            #     'blocks' : blocks_data
            # })
            data = json.dumps(
                blocks_data
            )

            response = requests.post(
                                    url=self.slack_webhook_chennel_url, 
                                    data=data,
                                    headers=header
                                )

            if response.status_code == 200:
                debugPrint("[+] Send message OK...")
            else:
                debugPrint("[+] Response ERR: {0}...".format(response.status_code))
                return ERRORCODE._SEND_MSG_FAIL

        except Exception as e:
            debugPrint("[-] Main Send function FAIL...")
            debugPrint("sendMsg funcing exception: {0}".format(e))

    def sendLiveMsg(self, live_datas, date, time, temp, ratio, url=""):
        try:
            debugPrint("[+] Send live message...")
            # load approval message form
            with open("msg_form.json", "rt", encoding='UTF8') as msg_f:
                msg_form = json.load(msg_f)

                # fill each data to msessage form
                # top field
                categorys = ["[date]", "[time]", "[temp]", "[ratio]"]
                datas = [date, time, temp, ratio]
                for category, data in zip(categorys, datas):
                    msg_form['blocks'][1]['text']['text'] = msg_form['blocks'][1]['text']['text'].replace(category, data)
                
                # list field
                msg_form['blocks'][3]['text']['text'] = "No\t이름\t동\t호\tMID\t온도\tratio1\tratio2\t전류\n"
                for live_data in live_datas:
                    print(live_data)
                    msg_form['blocks'][3]['text']['text'] += "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\n\n".format(
                                                            live_data['num'],live_data['name'],live_data['dong'],live_data['ho'],live_data['mid'], \
                                                            live_data['temp'],live_data['ratio1'],live_data['ratio2'],live_data['ampare'])
                    
                self.sendMsg(msg_form)
                debugPrint("[+] Send live message OK...")
        except Exception as e:
            debugPrint("[-] Send Live message FAIL...")
            debugPrint("sendLiveMsg funcing exception: {0}".format(e))




if __name__ == '__main__':
    test_Bot = Bot()

    test_data = [{'num': '1', 'name': '명륜현대1차', 'dong': '104', 'ho': '803', 'mid': 'A05370370', 'time': '23-08-21 11:00:00', 'temp': '44', 'ratio1': '3.63', 'ratio2': '15.17', 'ampare': '1'}]
    test_Bot.sendLiveMsg(test_data, date="23-08-21", time="11:00:00", temp="40", ratio="1.0")
    # test_Bot.sendApproveMsg("운동", "운동에 중요한 요소 5가지")
    # test_Bot.sendPostMsg("운동", "운동에 중요한 요소 5가지", 40, 0.14, url)

