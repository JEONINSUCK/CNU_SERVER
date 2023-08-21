from datetime import datetime
import enum


DEBUG_ENABLE = True

class ERRORCODE(enum.Enum):
    _SUCCESS = 1
    _THEME_EXIST = 2
    _THEME_NOT_EXIST = 3
    _TITLE_EXIST = 4
    _TITLE_ALL_USED = 5
    _REQUEST_GET_ERR = 6
    _CATEGORY_ID_NOT_EXIST = 7
    _SEND_MSG_FAIL = 8
    _SEND_MSG_ERR = 9
    _BODY_CHK_OK = 10
    _BODY_CHK_FAIL = 11
    _BODY_ACT_BUTTON = 12
    _BODY_ACT_INPUT = 13
    _THEME_DIR_NOT_EXIST = 14
    _THEME_FILE_NOT_EXIST = 15
    _THEME_FILE_EXIST = 16
    _TITLE_USED = 17
    _BT_DENY = 18
    _BT_INVALID = 19
    _BT_APPROVE = 20
    _QUERY_RES_ERR = 21
    _QUERY_FAIL = 22
    _BODY_CHK_CMD = 23
    _BODY_ACT_SELECT = 24
    _TITLE_DUPLI_ERR = 25
    _PARAM_ERR = 26
    
def debugPrint(data):
    if DEBUG_ENABLE:
        # get date & time
        now = datetime.now()
        today = now.date().strftime("%y-%m-%d")
        today_time = now.time().strftime("%H:%M:%S")
        print("{0} {1} > ".format(today, today_time), end="")
        print(data)