from fastapi import FastAPI, Header, Request, Response
from urllib import parse
from info_get import meterSort
from common import *
import schedule
import time
import json
import threading
import uvicorn

app = FastAPI()
temp = 48
ratio = 1.0

class webTool:
    def __init__(self) -> None:
        pass

    def getHeader(self, request: Request):
        return dict(request.headers.items())

    def getParm(self, request: Request):
        return dict(request.query_params.items())
    
async def getBody(request: Request):
    # get body from webhook request
    parse_request_body = await request.body()
    # convert bytes data to string data and decode
    parse_request_body= parse.unquote(parse_request_body.decode('utf-8')).replace("payload=", "").replace("+", " ")
    try:
        # convert str to json type
        conv_request_body = json.loads(parse_request_body)
    except Exception as e:
        parse_url = {}
        for data in parse_request_body.split("&"):
            tmp = data.split("=")
            parse_url[tmp[0]] = tmp[1]
        return parse_url
    return conv_request_body

        
@app.get("/")
async def get_test():
    return {"message" : "Hello world"}

# Request post operation
@app.post("/webhook", status_code=200)
async def webhook(request: Request):
    try:
        global temp
        web_t = webTool()
        meter_so = meterSort()
        th_live_seq = threading.Thread(target=meter_so.run, args=(temp, ratio))
        header = web_t.getHeader(request)
        parm = web_t.getParm(request)
        body = await getBody(request)

        try:
            if body['command'] == '/settemp':
                if body['text'] != '':
                    logger.info('[+] set temp slash command enter')
                    temp = int(body['text'])
                    th_live_seq.start()
                    return f"temp set success: {temp}"
                else:
                    logger.info('[-] set temp slash command ERROR')
                    return {"status": f"temp set fail: {temp}"}
            if body['command'] == '/listapt':
                if body['text'] != '':
                    logger.info('[+] list apartment slash command enter')
                    input_data = body['text'].split(" ")
                    if len(input_data)  == 4:
                        th_list_apt_seq = threading.Thread(target=meter_so.list_apt_seq, args=(input_data[0], input_data[1], input_data[2], input_data[3]))
                        th_list_apt_seq.start()
                        # meter_so.list_apt_seq(input_data[0], input_data[1], input_data[2], input_data[3])
                        return {"status": f"{input_data[0]}, {input_data[1]}, {input_data[2]}, {input_data[3]}"}
                    else:
                        logger.info('[-] list apartment slash command ERROR')
                        return {"status": f"input value wrong: {body['text']}"}    
                else:
                    return {"status": f"input value wrong: {body['text']}"}
        except Exception as e:
            logger.error(body)
            logger.error(f'body process err: {e}')
            return {"status": "body structure error"}
        

    except Exception as err:
        logger.error(await getBody(request))
        logger.error(f'could not print REQUEST: {err}')
        return {"status": "ERR"}


def scheduler_th():
    global temp, ratio

    logger.info("[+] Scheduler run...")
    meter_sort = meterSort()
    
    # to change the temp variable every time
    def sch_handler():
        meter_sort.run(temp, ratio)

    try:
        schedule.every().hour.at(":20").do(sch_handler)
        while(True):
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        logger.error('Ctrl + C 중지 메시지 출력')

def web_th():
    logger.info("[+] Web site run...")
    uvicorn.run(app, host="0.0.0.0", port=20001)


if __name__ == '__main__':
    # meter_sort = meterSort()
    # meter_sort.run(DEFUALT_TEMP, DEFUALT_RATIO)

    th_scheduler = threading.Thread(target=scheduler_th)
    th_web = threading.Thread(target=web_th)

    th_web.start()
    th_scheduler.start()