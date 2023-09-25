from datetime import datetime
try:
    from common import *
except Exception as e:
    from src.common import *
import json
import requests

SLACK_MSG_LIMIT = 3900

# load config.json data
with open("config.json", "r", encoding="utf-8-sig") as f:
    config = json.load(f)

logger = Mylogger()

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
                logger.info("[+] Send message OK...")
            else:
                logger.info("[+] Response ERR: {0}...".format(response.status_code))
                return ERRORCODE._SEND_MSG_FAIL

        except Exception as e:
            logger.error("[-] Main Send function FAIL...")
            logger.error("sendMsg funcing exception: {0}".format(e))

    def sendRatioMsg(self, live_datas, date, time, temp, ratio, url=""):
        try:
            logger.info("[+] Send ratio message run...")
            # load approval message form
            with open("src/msg_form.json", "rt", encoding='UTF8') as msg_f:
                msg_form = json.load(msg_f)

                # fill each data to msessage form
                # top field
                categorys = ["[date]", "[time]시", "[temp]", "[ratio]"]
                datas = [date, time, temp, ratio]
                for category, data in zip(categorys, datas):
                    msg_form['attachments'][0]['blocks'][1]['text']['text'] = msg_form['attachments'][0]['blocks'][1]['text']['text'].replace(category, data)
                
                if len(live_datas['new']) != 0 or len(live_datas['before']) != 0:
                    # NEW list field
                    msg_form['attachments'][0]['blocks'][4]['text']['text'] = "No\t\t날짜\t\t이름\t\t동\t\t호\t\tMID\t\t온도\t\tratio1\t\tratio2\n\n\n"
                    i = 1
                    for live_data in live_datas['new']:
                        msg_form['attachments'][0]['blocks'][4]['text']['text'] += "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\n\n".format(
                                                                i,live_data['time'],live_data['name'],live_data['dong'],live_data['ho'],live_data['mid'], \
                                                                live_data['temp'],live_data['ratio1'],live_data['ratio2'])
                        i = i + 1
                    
                    # BEFORE list field
                    msg_form['attachments'][0]['blocks'][7]['text']['text'] = "No\t\t날짜\t\t이름\t\t동\t\t호\t\tMID\t\t온도\t\tratio1\t\tratio2\n\n\n"
                    i = 1
                    for live_data in live_datas['before']:
                        msg_form['attachments'][0]['blocks'][7]['text']['text'] += "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\n\n".format(
                                                                i,live_data['time'],live_data['name'],live_data['dong'],live_data['ho'],live_data['mid'], \
                                                                live_data['temp'],live_data['ratio1'],live_data['ratio2'])
                        i = i + 1


                    # url set
                    if url != "":
                        msg_form['attachments'][0]['blocks'][9]['elements'][0]['url'] = url

                if self.count_text(msg_form) < SLACK_MSG_LIMIT:
                    self.sendMsg(msg_form)
                    logger.info("[+] Send ratio message OK...")
                else:
                    pass
        except Exception as e:
            logger.error("[-] Send ratio message FAIL...")
            logger.error("sendRatioMsg funcing exception: {0}".format(e))

    def sendLiveMsg(self, live_datas, date, time, temp, url=""):
        try:
            logger.info("[+] Send live message...")
            # load approval message form
            with open("src/msg_form.json", "rt", encoding='UTF8') as msg_f:
                msg_form = json.load(msg_f)

                # fill each data to msessage form
                # top field
                categorys = ["[date]", "[time]", "[temp]", "[ratio] 이상"]
                datas = [date, time, temp, ""]
                for category, data in zip(categorys, datas):
                    msg_form['attachments'][0]['blocks'][1]['text']['text'] = msg_form['attachments'][0]['blocks'][1]['text']['text'].replace(category, data)
                
                # NEW list field
                msg_form['attachments'][0]['blocks'][4]['text']['text'] = "No\t이름\tMID\t온도\n"
                i = 1
                for live_data in live_datas['new']:
                    msg_form['attachments'][0]['blocks'][4]['text']['text'] += "{0}\t{1}\t{2}\t{3}\n\n".format(
                                                            i,live_data['name'],live_data['mid'],live_data['temp'])
                    i = i + 1

                # BEFORE list field
                msg_form['attachments'][0]['blocks'][7]['text']['text'] = "No\t이름\tMID\t온도\n"
                i = 1
                for live_data in live_datas['before']:
                    msg_form['attachments'][0]['blocks'][4]['text']['text'] += "{0}\t{1}\t{2}\t{3}\n\n".format(
                                                            i,live_data['name'],live_data['mid'],live_data['temp'])
                    i = i + 1

                # url set
                if url != "":
                    msg_form['attachments'][0]['blocks'][9]['elements'][0]['url'] = url


                if self.count_text(msg_form) < SLACK_MSG_LIMIT:
                    self.sendMsg(msg_form)
                    logger.info("[+] Send live message OK...")
                else:
                    pass
        except Exception as e:
            logger.error("[-] Send live message FAIL...")
            logger.error("sendLiveMsg funcing exception: {0}".format(e))

    def count_text(self, data):
        try:
            logger.info("[+] Count text run...")
            if type(data) is not dict:
                return ERRORCODE._TYPE_ERR
            
            # search the value from every node
            def search_node(node, key):
                if isinstance(node, list):
                    for i in node:
                        for x in search_node(i, key):
                            yield x
                elif isinstance(node, dict):
                    if key in node:                         
                        # if isinstance(node[key], str):        # 상위에 같은 key가 있을 경우 하위 키만 반환 함
                        yield node[key]
                        # else:
                        #     search_node(node[key], key)
                    else:         # 하위에 같은 key가 있는지 확인 안함(else 빼면 확인 함)
                        for j in node.values():
                            for x in search_node(j, key):
                                yield x

            cnt = 0

            for tmp in list(search_node(data, 'text')):
                # print(tmp)
                cnt += len(str(tmp))
            
            logger.info(f"[+] Text len: {cnt}")
            return cnt
                
        except Exception as e:
            logger.error("[-] Count text FAIL...")
            logger.error("count_text funcing exception: {0}".format(e))

    # def excel_store()

if __name__ == '__main__':
    test_Bot = Bot()

    test_data = {'new': [
{'num': '1', 'name': '중앙주공9단지', 'mid': 'A0537006033', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '2', 'name': '중앙주공9단지', 'mid': 'A0537006757', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '3', 'name': '중앙주공9단지', 'mid': 'A0537007091', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '4', 'name': '중앙주공9단지', 'mid': 'A0537008291', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '5', 'name': '중앙주공9단지', 'mid': 'A0537008316', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '6', 'name': '중앙주공9단지', 'mid': 'A0537008402', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '7', 'name': '중앙주공9단지', 'mid': 'A0537008610', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '8', 'name': '중앙주공9단지', 'mid': 'A0537008873', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '9', 'name': '중앙주공9단지', 'mid': 'A0537008887', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '10', 'name': '석사2지구', 'mid': 'A0537026008', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '11', 'name': '석사2지구', 'mid': 'A0537030769', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '12', 'name': '석사2지구', 'mid': 'A0537030902', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '13', 'name': '석사2지구', 'mid': 'A0537031106', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '15', 'name': '상계주공7단지', 'mid': 'A0537032531', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '16', 'name': '상계주공7단지', 'mid': 'A0537034496', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '17', 'name': '상계주공7단지', 'mid': 'A0537034832', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '18', 'name': '우만주공4단지', 'mid': 'A0537081613', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '19', 'name': '우만주공4단지', 'mid': 'A0537098005', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '20', 'name': '우만주공4단지', 'mid': 'A0537098158', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '21', 'name': '우만주공4단지', 'mid': 'A0537098507', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '22', 'name': '우만주공4단지', 'mid': 'A0537102778', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '23', 'name': '부평현대2단지', 'mid': 'A0537104634', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '24', 'name': '부평현대2단지', 'mid': 'A0537105736', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '25', 'name': '부평현대2단지', 'mid': 'A0537113437', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '26', 'name': '도두리마을동남롯데', 'mid': 'A0537113735', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '27', 'name': '도두리마을동남롯데', 'mid': 'A0537115674', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '28', 'name': '부평현대2단지', 'mid': 'A0537116196', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '29', 'name': '부평현대2단지', 'mid': 'A0537116518', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '30', 'name': '부평현대2단지', 'mid': 'A0537117006', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '31', 'name': '부평현대2단지', 'mid': 'A0537117014', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '32', 'name': '부평현대2단지', 'mid': 'A0537117569', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '33', 'name': '부평현대2단지', 'mid': 'A0537117579', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '34', 'name': '부평현대2단지', 'mid': 'A0537117723', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '35', 'name': '부평현대2단지', 'mid': 'A0537117991', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '36', 'name': '부평현대2단지', 'mid': 'A0537117996', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '37', 'name': '부평현대2단지', 'mid': 'A0537118031', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '38', 'name': '부평현대2단지', 'mid': 'A0537118165', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '39', 'name': '부평현대2단지', 'mid': 'A0537118194', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '40', 'name': '우만주공4단지', 'mid': 'A0537118458', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '41', 'name': '부평현대2단지', 'mid': 'A0537118505', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '42', 'name': '부평현대2단지', 'mid': 'A0537118544', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '43', 'name': '부평현대2단지', 'mid': 'A0537118549', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '44', 'name': '부평현대2단지', 'mid': 'A0537118555', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '45', 'name': '부평현대2단지', 'mid': 'A0537118619', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '46', 'name': '부평현대2단지', 'mid': 'A0537118750', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '47', 'name': '부평현대2단지', 'mid': 'A0537118825', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '48', 'name': '부평현대2단지', 'mid': 'A0537118904', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '49', 'name': '부평현대2단지', 'mid': 'A0537119729', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '50', 'name': '부평현대2단지', 'mid': 'A0537119777', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '51', 'name': '나주송월부영2차', 'mid': 'A0537130809', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '52', 'name': '나주송월부영2차', 'mid': 'A0537134249', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '53', 'name': '나주송월부영2차', 'mid': 'A0537138676', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '54', 'name': '산곡5차현대', 'mid': 'A0537154221', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '55', 'name': '화정은빛마을11단지', 'mid': 'A0537159210', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '56', 'name': '화정은빛마을11단지', 'mid': 'A0537159322', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '57', 'name': '화정은빛마을11단지', 'mid': 'A0537159344', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '58', 'name': '화정은빛마을11단지', 'mid': 'A0537159487', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '59', 'name': '화정은빛마을11단지', 'mid': 'A0537160158', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '60', 'name': '화정은빛마을11단지', 'mid': 'A0537160383', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '61', 'name': '화정은빛마을11단지', 'mid': 'A0537161905', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '62', 'name': '화정은빛마을11단지', 'mid': 'A0537161922', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '63', 'name': '화정은빛마을11단지', 'mid': 'A0537161941', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '64', 'name': '화정은빛마을11단지', 'mid': 'A0537165354', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '65', 'name': '화정은빛마을11단지', 'mid': 'A0537165487', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '66', 'name': '화정은빛마을11단지', 'mid': 'A0537165782', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '67', 'name': '화정은빛마을11단지', 'mid': 'A0537165784', 'time': '2023-09-22 18:00:00', 'temp': '45'}
, {'num': '68', 'name': '중앙주공9단지', 'mid': 'A0537005508', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '69', 'name': '중앙주공9단지', 'mid': 'A0537008058', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '70', 'name': '중앙주공9단지', 'mid': 'A0537008141', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '71', 'name': '중앙주공9단지', 'mid': 'A0537008401', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '72', 'name': '중앙주공9단지', 'mid': 'A0537008418', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '73', 'name': '중앙주공9단지', 'mid': 'A0537008881', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '74', 'name': '중앙주공9단지', 'mid': 'A0537008882', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '75', 'name': '상계주공7단지', 'mid': 'A0537041119', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '76', 'name': '상계주공7단지', 'mid': 'A0537041123', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '77', 'name': '우만주공4단지', 'mid': 'A0537083365', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '78', 'name': '우만주공4단지', 'mid': 'A0537098015', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '79', 'name': '우만주공4단지', 'mid': 'A0537101491', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '80', 'name': '부평현대2단지', 'mid': 'A0537105615', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '81', 'name': '우만주공4단지', 'mid': 'A0537105800', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '82', 'name': '상계주공7단지', 'mid': 'A0537108289', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '83', 'name': '도두리마을동남롯데', 'mid': 'A0537111735', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '84', 'name': '부평현대2단지', 'mid': 'A0537112134', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '85', 'name': '부평현대2단지', 'mid': 'A0537112154', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '86', 'name': '부평현대2단지', 'mid': 'A0537113424', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '87', 'name': '부평현대2단지', 'mid': 'A0537116199', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '88', 'name': '부평현대2단지', 'mid': 'A0537117015', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '89', 'name': '부평현대2단지', 'mid': 'A0537117335', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '90', 'name': '부평현대2단지', 'mid': 'A0537117995', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '91', 'name': '부평현대2단지', 'mid': 'A0537118190', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '92', 'name': '부평현대2단지', 'mid': 'A0537118504', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '93', 'name': '부평현대2단지', 'mid': 'A0537118607', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '94', 'name': '부평현대2단지', 'mid': 'A0537118610', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '95', 'name': '부평현대2단지', 'mid': 'A0537118746', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '96', 'name': '부평현대2단지', 'mid': 'A0537118748', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '97', 'name': '부평현대2단지', 'mid': 'A0537118756', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '98', 'name': '부평현대2단지', 'mid': 'A0537118818', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '99', 'name': '부평현대2단지', 'mid': 'A0537118928', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '100', 'name': '부평현대2단지', 'mid': 'A0537119676', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '101', 'name': '부평현대2단지', 'mid': 'A0537119678', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '102', 'name': '부평현대2단지', 'mid': 'A0537119679', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '103', 'name': '부평현대2단지', 'mid': 'A0537119779', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '104', 'name': '우만주공4단지', 'mid': 'A0537137779', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '105', 'name': '화정은빛마을11단지', 'mid': 'A0537156352', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '106', 'name': '화정은빛마을11단지', 'mid': 'A0537159227', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '107', 'name': '화정은빛마을11단지', 'mid': 'A0537159304', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '108', 'name': '화정은빛마을11단지', 'mid': 'A0537159345', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '109', 'name': '화정은빛마을11단지', 'mid': 'A0537159500', 'time': '2023-09-22 18:00:00', 'temp': '46'}
, {'num': '110', 'name': '화', 'mid': 'A053000', 'time': '2023-09-22 18:00:00', 'temp': '46'}
], 'before': []}




    test_Bot.sendLiveMsg(test_data, date="23-08-21", time="11:00:00", temp="40")
    # print(test_Bot.count_text(test_data))
    
