from utils.synfile import WebDavCookies 
from threading import Thread
import datetime
import time
import json
import os
 

class TimerThread:
    """ 定时执行类，允许前后10分钟的误差内执行
        - 例如 定时执行 函数 hello("你好","中国")   

        ``` spect = [8, 30, 0]
            t = TimerThread()   
            t.add_job(spect, hello, "你好", "中国")
        ```   
    """
    def __circlerun(self, spect, func, *args):
        spctime = timeFormat(spect)
        inrange = timeRange(spect, 10)
        # 允许指定时间的前后10分钟内执行
        if inrange:
            while True:
                nowtime = datetime.datetime.now()
                if spctime<=nowtime:
                    func(*args)
                    otm = f'{nowtime}'
                    return otm

    def addjob(self, spectime:str, func, *args):
        """
            - timeee: 指定时间，如 [08,30,00]
            - func: 函数名称
            - args: 函数 func 的参数
        """
        # self.__circlerun(spectime, func, *args)
        t = Thread(target=self.__circlerun, args=(spectime, func, *args))
        t.start()
        t.join()
 

def writeJson(path_pair, file):
    with open(path_pair[0], "w") as f:
        json.dump(file, f)
    WebDavCookies.up_cookies(path_pair)


def openJson(path)-> dict:
    try:
        with open(path, "r") as f: 
            return json.load(f)
    except:
        return None


def makePath(path: str):
 
    if not os.path.exists(path):
        os.makedirs(path)
 

def timerRun(intime):
    """ 定时运行装饰器，定义函数时装饰指定时间 """
    def wrapper(func):
        def deco(*args, **kwargs):
            while True:
                if intime <= time.strftime("%H:%M:%S", time.localtime()):
                    func(*args, **kwargs)
                    break
        return deco
    return wrapper


def timeFormat(spect:list):
    today  = datetime.datetime.now()
    timefmat = datetime.datetime(today.year, today.month, today.day, *spect)
    return timefmat


def timeRange(spect:list, delta:int):
    """  时间范围，[h, m, s, μs]
        - 如8点前后5分钟
        - spect=[8,0,0]，delta=5
        - @return 是否在指定时间范围
    """
    spctime = timeFormat(spect)
    nowtime = datetime.datetime.now()
    deltime = nowtime - spctime

    inrange = abs(deltime) < datetime.timedelta(minutes=delta)

    return inrange


def isOverTime(spect:list):
    """ 是否超过某时间 
        时间范围，[h, m, s, μs]
    """
    spctime = timeFormat(spect)
    nowtime = datetime.datetime.now()
 
    return nowtime > spctime