from library.manager import ReserveManager 
from utils.synfile import WebDavCookies 
from library.consts import *
from config.config import *
 

def initializer(event=None):
    """ 提前初始化数据 """
    # WebDavCookies.down_cookies()
    pass


def handler(event=None, text=None):
    """ 程序总控入口 """ 
    
    # 将需要预约的用户加入列表
    USRLST = [USER_NAME1, USER_NAME2]
 
    res = ReserveManager(USRLST)
    res.printLogs()
    res.pushLogs("wxpush", [7,0,0], title=" 🔵 程序预约日志-服务器C(本地)")          
 
 
if __name__ == '__main__':
    
    handler()
    # handler()