from bs4 import BeautifulSoup
from slack_bot import Bot
import requests
import json
import schedule
import time
import threading
from datetime import datetime

USERNAME = "admin"
PASSOWRD = "cnuasdcu"
DEFUALT_DAY = 1
DEFUALT_TEMP = 45
DEFUALT_RATIO = 1.0
DEFUALT_CNT = 3


class infoGet:
    def __init__(self):
        self.temp_cnt_url = "http://211.170.156.163/temp/temperatureCount.php?"
        self.detail_search_url = "http://211.170.156.163/temp/json/procSelectInstantDay.php?"
        self.temp_meter_url = "http://211.170.156.163/temp/temperatureMeter.php?"
        self.emis_url = "http://management.scityplatform.co.kr/cnu/html/load_profile.html"
        self.ratio_url = "http://211.170.156.163/temp/RDB2_ratio.php?"
        self.session = requests.Session()
        self.auth = requests.auth.HTTPBasicAuth(USERNAME, PASSOWRD)

    def get_cnt_list(self, p_did="", p_day=DEFUALT_DAY, p_temp=DEFUALT_TEMP, p_cnt=DEFUALT_CNT):
        keys = ['num', 'name', 'mid', 'cnt']

        
        try:
            qeury = f"{self.temp_cnt_url}&p_did={p_did}&p_day={p_day}&p_temp={p_temp}&p_cnt={p_cnt}"
            res = requests.get(qeury, auth=self.auth)

            result_list = self.cnu_parser(res, keys)

            return result_list
        except Exception as e:
            print(f'get_cnt_list function ERR: {e}')

        
    def get_ratio_list(self, p_date, p_time, p_temp, p_ratio, p_did=""):
        keys = ['num', 'name', 'dong', 'ho', 'mid', 'time', 'temp', 'ratio1', 'ratio2', 'ampare']

        try:
            qeury = f"{self.ratio_url}&p_did={p_did}&p_date={p_date}&p_time={p_time}&p_temp={p_temp}&p_ratio={p_ratio}"
            res = requests.get(qeury, auth=self.auth)

            result_list = self.cnu_parser(res, keys)

            return result_list
        
        except Exception as e:
            print(f'get_ratio_list function ERR: {e}')


    def cnu_parser(self, res, keys):
        result_buf = []

        bs = BeautifulSoup(res.text, 'html.parser')
        tag = bs.find('td', attrs={'class': 'tdBody'}).find('tbody')

        for items in tag.find_all('tr'):
            item = items.find_all('td')
            if item != None:
                data_format = {}
                for key, data in zip(keys, item):
                    data_format[key] = data.get_text()
                result_buf.append(data_format)
        return result_buf

    def post_list(self, p_mid, p_day=1):
        form_data = {
            'p_mid' : p_mid,
            'p_day' : p_day
        }
        
        try:
            res = requests.post(self.detail_search_url, auth=self.auth, data=form_data)
            res = json.loads(res.text)
            if res['msg'] == 'success':
                return res.get('data')
            else:
                return -1
        except Exception as e:
            print(f'post_list function ERR: {e}')

class meterSort:
    def __init__(self):
        self.info_get = infoGet()
        self.slack_bot = Bot()

    def run(self, temp, ratio):
         # get date & time
        now = datetime.now()
        date_val = now.date().strftime("%Y-%m-%d")
        time_val = now.time().strftime("%H:00:00")
        temp_val = temp
        ratio_val = ratio
        fourty_five_list = self.info_get.get_cnt_list()
        fifty_list = self.info_get.get_cnt_list(p_temp=50, p_cnt=1)

        hour_datas = self.info_get.post_list(p_mid=fourty_five_list[0].get('mid'))
        live_datas = self.info_get.get_ratio_list(date_val, time_val, temp_val, ratio_val)
        self.slack_bot.sendLiveMsg(live_datas, date_val, str(time_val), str(temp_val), str(ratio_val))

def scheduler_th():
    print("[+] Scheduler run...")
    meter_sort = meterSort()
    def test_th():
        print("test")
    try:
        # schedule.every().hour.at(":03").do(meter_sort.run(DEFUALT_TEMP, DEFUALT_RATIO))
        schedule.every().hour.at(":31").do(test_th)
        while(True):
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        print('Ctrl + C 중지 메시지 출력')

if __name__ == '__main__':
    # meter_sort = meterSort()
    # meter_sort.run(DEFUALT_TEMP, DEFUALT_RATIO)

    th_scheduler = threading.Thread(target=scheduler_th)
    th_scheduler.start()

