from bs4 import BeautifulSoup
from slack_bot import Bot
from urllib import parse
import pandas as pd
import requests
import json

import time
from datetime import datetime, timedelta
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
        self.detail_search_url = "http://211.170.156.163/temp/json/procSelectInstant.php"
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
        debugPrint(f"[+] Get {p_date} {p_time}시 Ratio list run...")
        keys = ['num', 'name', 'dong', 'ho', 'mid', 'time', 'temp', 'ratio1', 'ratio2', 'ampare']

        try:
            qeury = f"{self.ratio_url}&p_did={p_did}&p_date={p_date}&p_time={p_time}&p_temp={p_temp}&p_ratio={p_ratio}"
            res = requests.get(qeury, auth=self.auth)
            if res.status_code == 200:
                result_list = self.cnu_parser(res, keys)
                if result_list == ERRORCODE._NO_DATA:
                    # debugPrint("[+] NO Live data...")
                    return { 'data' : ERRORCODE._NO_DATA }
                
                debugPrint(f"[+] Get {p_date} {p_time}시 Ratio list OK...")
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
        debugPrint(f'date: {p_date}, time: {p_time}, temp: {p_temp}')
        keys = ['num', 'name', 'mid', 'time', 'temp']

        try:
            qeury = f"{self.live_url}&p_did={p_did}&p_temp={p_temp}"
            res = requests.get(qeury, auth=self.auth)
            if res.status_code == 200:
                result_list = self.cnu_parser(res, keys)
                if result_list == ERRORCODE._NO_DATA:
                    debugPrint("[+] NO Live data...")
                    return { 'data' : ERRORCODE._NO_DATA }

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

    def get_detail_temp_list(self, mid, date):
        debugPrint("[+] Get Detail Temp list run...")
        payload = {
                "p_mid" : mid,
                "p_time" : date
            }
        try:
            res = requests.post(self.detail_search_url, data=payload, auth=self.auth)
            if res.status_code == 200:
                res = json.loads(res.text)
                if res['msg'] == 'success':
                    detail_datas = res['data']
                    debugPrint("[+] Get Detail Temp list OK...")
                    return { 'data' : detail_datas }
                else:
                    return { 'data' : ERRORCODE._NO_POST_DATA }

        except Exception as e:
            print(f'get_detail_temp_list function ERR: {e}')
            debugPrint("[-] Get Detail Temp list FAIL...")

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

    def post_list(self, p_mid, p_time):
        form_data = {
            'p_mid' : p_mid,
            'p_time' : p_time
        }
        
        try:
            res = requests.post(self.live_url, auth=self.auth, data=form_data)
            res = json.loads(res.text.decode())
            if res['msg'] == 'success':
                return res.get('data')
            else:
                return -1
        except Exception as e:
            print(f'post_list function ERR: {e}')

    def get_dcu_id(self, apt_name):
        debugPrint("[+] get_dcu_id run...")
        try:
            qeury = f"{self.live_url}&p_did=&p_temp=48"
            res = requests.get(qeury, auth=self.auth)
            if res.status_code == 200:
                bs = BeautifulSoup(res.text, 'html.parser')
                try:
                    # tag = bs.find('td', attrs={'class': 'tdBody'}).find('tbody')
                    tag = bs.find('select', attrs={'name': 'p_did'})
                    for items in tag.find_all('option'):
                        dcu_info = items.get_text()
                        if dcu_info.find(apt_name) != -1:
                            debugPrint("[+] get_dcu_id OK...")
                            return items['value']
                        
                except Exception as e:
                    debugPrint("[-] HTML response has no body")
                    return ERRORCODE._QUERY_FAIL
        except Exception as e:
            print(f'get_dcu_id function ERR: {e}')
            debugPrint("[-] get_dcu_id FAIL...")

    def dupli_chk(self, src):
        try:
            debugPrint("[+] Duplication Check Run...")
            sample1 = pd.read_excel("data/계량기_점검_교체_리스트_통합.xlsx", sheet_name='점검리스트', usecols='F,M')
            sample2 = pd.read_excel("data/계량기_점검_교체_리스트_통합.xlsx", sheet_name='요청리스트', usecols='D,H')
            read_data = pd.concat([sample1, sample2])

            result = {'new': [], 'before': []}
            if len(src) != 0:
                for target in src:
                    filter_data = read_data[read_data['미터 ID'].str.contains(target['mid'], na=False)]
                    if len(filter_data) != 0:
                        result['before'].append(target)
                    else:
                        result['new'].append(target)
                
                debugPrint("[+] Duplication Check OK...")
                return result
            
            return ERRORCODE._DUPLI_FAIL
        
        except Exception as e:
            print(f'dupli_chk function ERR: {e}')
            debugPrint("[-] Duplication Check FAIL...")

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
        
        # time_val = "17:00:00"

        result_data = self.info_get.get_live_list(date_val, time_val, temp)
        if result_data['data'] == ERRORCODE._NO_DATA:
            pass
        elif result_data['data'] == ERRORCODE._SEND_MSG_ERR:
            pass
        else:
            filter_data = self.info_get.dupli_chk(result_data['data'])
            debugPrint(filter_data)
            self.slack_bot.sendLiveMsg(filter_data, date_val, time_val, str(temp_val), url=result_data['url'])

    def list_apt_seq(self, apt_name, temp, ratio, day_cnt):
        try:
            result_data = []
            mid_data = []
            # get date & time
            now = datetime.now()
            temp_val = temp
            ratio_val = ratio
            dcu_id = self.info_get.get_dcu_id(apt_name)

            for i in range(int(day_cnt)):
                date_val = now - timedelta(days=i)
                date_val = date_val.date().strftime("%Y%m%d")
                for time_val in range(24):
                    time_datas = self.info_get.get_ratio_list(p_did=dcu_id, p_date=date_val, p_time=time_val, 
                                                            p_temp=temp_val, p_ratio=ratio_val)['data']
                    if time_datas == ERRORCODE._NO_DATA:
                        continue
                    else:
                        for time_data in time_datas:
                            if time_data['mid'] in mid_data:
                                continue
                            else:
                                mid_data.append(time_data['mid'])
                                result_data.append(time_data)
            if len(result_data) != 0:
                filter_data = self.info_get.dupli_chk(result_data)
                debugPrint(filter_data)
                self.slack_bot.sendRatioMsg(filter_data, now.date().strftime("%Y%m%d"), f"{day_cnt}일 치", str(temp_val), str(ratio_val))
            else:
                self.slack_bot.sendRatioMsg({'new': [], 'before': []}, now.date().strftime("%Y%m%d"), f"{day_cnt}일 치", str(temp_val), str(ratio_val))
        except Exception as e:
            print(f'list_apt_seq function ERR: {e}')
            debugPrint("[-] List apartment sequence FAIL...")

    def test(self, apt_name, temp, ratio):
        
        time_val = 10
        date_val = datetime.now().date().strftime("%Y%m%d")
        dcu_id = self.info_get.get_dcu_id(apt_name)
        time_datas = self.info_get.get_ratio_list(p_did=dcu_id, p_date=date_val, p_time=time_val, 
                                                            p_temp=temp, p_ratio=ratio)['data']
        return time_datas

    def run(self, temp, ratio):
        debugPrint("[+] CNU server sort Run...")
        try:
            # ration sequence run
            # self.ratio_monitor_seq(temp, ratio)

            # live sequence run
            self.live_monitor_seq(temp)


            debugPrint("[+] CNU server sort OK...")
        except Exception as e:
            debugPrint("[-] CNU server sort FAIL...")
            debugPrint(f"CNU server sort ERR: {e}")


if __name__ == '__main__':
    meter_sort = meterSort()
    info_get = infoGet()
    # meter_sort.run(DEFUALT_TEMP, DEFUALT_RATIO)
    p_mid = 'A0537049493'
    p_time = '2023-08-25 16:00:00'
    # print(info_get.post_list(p_mid, p_time))
    # print(info_get.get_dcu_id("명륜현대1차"))
    # meter_sort.list_apt_seq("푸른마을신안실크밸리1차", 32, 2.0, 1)
    # meter_sort.live_monitor_seq(38)

    # info_get.get_detail_temp_list('A0537089514', '2023-09-12 10:00:00')
    # tmp_data = meter_sort.test("계룡리슈빌", 30, 1.0)
    # print(len(info_get.get_detail_temp_list(tmp_data[0]['mid'], tmp_data[0]['time'])['data']))
    
    # th_scheduler = threading.Thread(target=scheduler_th)
    # th_scheduler.start()

    # now = datetime.now()
    # date_val = now.date().strftime("%Y-%m-%d")
    # time_val = now.time().strftime("%H:00:00")
    # print(info_get.get_live_list(date_val, time_val, 43))
    sample_data = info_get.get_live_list('2023-09-16', '11:00:00', 40)['data']
    sample_data.append({'mid' : 'A0537096323'})
    sample_data.append({'mid' : 'A0537129033'})
    print(info_get.dupli_chk(sample_data))