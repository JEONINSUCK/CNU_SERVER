from datetime import datetime
import enum
import logging


class Mylogger:
    def __init__(self) -> None:
        self.log = logging.getLogger('cnu_log')
        self.formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)s] >> %(message)s')
        self.streamHandler = logging.StreamHandler()
        self.fileHandler = logging.FileHandler('./history.log')
        self.streamHandler.setFormatter(self.formatter)
        self.fileHandler.setFormatter(self.formatter)

    def info(self, data):
        self.log.handlers.clear()
        self.log.addHandler(self.streamHandler)
        self.log.addHandler(self.fileHandler)
        self.log.setLevel(level=logging.INFO)

        self.log.info(data)

    def debug(self, data):
        self.log.handlers.clear()
        self.log.addHandler(self.fileHandler)
        self.log.setLevel(level=logging.DEBUG)
        
        self.log.debug(data)

    def error(self, data):
        self.log.handlers.clear()
        self.log.addHandler(self.streamHandler)
        self.log.addHandler(self.fileHandler)
        self.log.setLevel(level=logging.INFO)

        self.log.error(data)

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
    _NO_DATA = 27
    _NO_POST_DATA = 28
    _DUPLI_FAIL = 29
    _DCU_ID_NOT_FOUND = 30
    _BLACK_CHK_FAIL = 31
    _TYPE_ERR = 32
    
if __name__ == '__main__':
    Mylogger().info('info test')
    Mylogger().debug('debug test')
    Mylogger().error('error test')