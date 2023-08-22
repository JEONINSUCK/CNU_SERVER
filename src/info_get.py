from bs4 import BeautifulSoup
from slack_bot import Bot
import requests
import json
import schedule
import time
import threading
from datetime import datetime
from common import *

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
        self.live_url = "http://211.170.156.163/temp/temperature.php?"
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
        debugPrint("[+] Get Ratio list run...")
        keys = ['num', 'name', 'dong', 'ho', 'mid', 'time', 'temp', 'ratio1', 'ratio2', 'ampare']

        try:
            qeury = f"{self.ratio_url}&p_did={p_did}&p_date={p_date}&p_time={p_time}&p_temp={p_temp}&p_ratio={p_ratio}"
            res = requests.get(qeury, auth=self.auth)
            if res.status_code == 200:
                result_list = self.cnu_parser(res, keys)

                debugPrint("[+] Get Ratio list OK...")
                return { 'data': result_list, 'url' : qeury}
            else:
                debugPrint("[+] Response ERR: {0}...".format(res.status_code))
                return ERRORCODE._SEND_MSG_FAIL
            
        except Exception as e:
            print(f'get_ratio_list function ERR: {e}')
            debugPrint("[-] Get Ratio list FAIL...")
            

    def get_live_list(self, p_date, p_time, p_temp, p_did=""):
        result_data = []
        debugPrint("[+] Get Live list run...")
        keys = ['num', 'name', 'mid', 'time', 'temp']

        try:
            qeury = f"{self.live_url}&p_did={p_did}&p_temp={p_temp}"
            res = requests.get(qeury, auth=self.auth)
            if res.status_code == 200:
                result_list = self.cnu_parser(res, keys)

                for each_data in result_list:    
                    date_time = each_data['time'].split(" ")
                    if date_time[0] == p_date and date_time[1] == p_time:
                        result_data.append(each_data)

                if len(result_data) != 0:    
                    debugPrint("[+] Get Live list OK...")
                    return { 'data': result_data, 'url' : qeury}
                else:
                    debugPrint("[+] NO Live data...")
                    return { 'data' : ERRORCODE._NO_DATA }
            else:
                debugPrint("[+] Response ERR: {0}...".format(res.status_code))
                return ERRORCODE._SEND_MSG_FAIL
            
        except Exception as e:
            print(f'get_live_list function ERR: {e}')
            debugPrint("[-] Get Live list FAIL...")



    def cnu_parser(self, res, keys):
        debugPrint("[+] CNU Parser run...")
        result_buf = []
        try:
            bs = BeautifulSoup(res.text, 'html.parser')
            try:
                # tag = bs.find('td', attrs={'class': 'tdBody'}).find('tbody')
                tag = bs.find('td', attrs={'class': 'tdBody'}).find('tbody')
            except Exception as e:
                debugPrint("[-] HTML response has no body")
                return ERRORCODE._QUERY_FAIL
            
            if len(tag.find_all('tr')) == 0:
                debugPrint("[+] NO searching data...")
                return ERRORCODE._NO_DATA
            
            for items in tag.find_all('tr'):
                item = items.find_all('td')
                if item != None:
                    data_format = {}
                    for key, data in zip(keys, item):
                        data_format[key] = data.get_text()
                    result_buf.append(data_format)
            debugPrint("[+] CNU Parser OK...")
            return result_buf
        except Exception as e:
            print(f'cnu_parser function ERR: {e}')
            debugPrint("[-] CNU Parser FAIL...")

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

    def ratio_monitor_seq(self, temp, ratio):
        try:
            # get date & time
            now = datetime.now()
            date_val = now.date().strftime("%Y%m%d")
            time_val = now.time().strftime("%H")
            temp_val = temp
            ratio_val = ratio
            debugPrint("[+] Ratio monitoring sequence Run...")

            live_datas = self.info_get.get_ratio_list(date_val, 10, temp_val, ratio_val)
            if live_datas['data'] != ERRORCODE._NO_DATA:
                self.slack_bot.sendRatioMsg(live_datas['data'], date_val, str(time_val), str(temp_val), str(ratio_val), url=live_datas['url'])
            else:
                debugPrint("[+] Server No Data...")
            
            debugPrint("[+] Ratio monitoring sequence OK...")
        except Exception as e:
            debugPrint("[-] Ratio monitoring sequence FAIL...")

    def live_monitor_seq(self, temp):
        # get date & time
        now = datetime.now()
        date_val = now.date().strftime("%Y-%m-%d")
        time_val = now.time().strftime("%H:00:00")
        temp_val = temp

        result_data = self.info_get.get_live_list(date_val, time_val, temp)
        if result_data['data'] == ERRORCODE._NO_DATA:
            pass
        elif result_data['data'] == ERRORCODE._SEND_MSG_ERR:
            pass
        else:
            self.slack_bot.sendLiveMsg(result_data['data'], date_val, time_val, str(temp_val), url=result_data['url'])

    def run(self, temp, ratio):
        debugPrint("[+] MeterSort Run...")
        try:
            # ration sequence run
            # self.ratio_monitor_seq(temp, ratio)

            # live sequence run
            self.live_monitor_seq(48)


            debugPrint("[+] MeterSort Run OK...")
        except Exception as e:
            debugPrint("[-] MeterSort FAIL...")
            debugPrint(f"run function ERR: {e}")


def scheduler_th():
    print("[+] Scheduler run...")
    meter_sort = meterSort()

    try:
        schedule.every().hour.at(":02").do(meter_sort.run,DEFUALT_TEMP, DEFUALT_RATIO)
        while(True):
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        print('Ctrl + C 중지 메시지 출력')

if __name__ == '__main__':
    meter_sort = meterSort()
    meter_sort.run(DEFUALT_TEMP, DEFUALT_RATIO)

    # th_scheduler = threading.Thread(target=scheduler_th)
    # th_scheduler.start()

