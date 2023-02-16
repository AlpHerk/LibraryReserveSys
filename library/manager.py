import time
from queue import Queue
from threading import Thread
from typing import List

from control import reserveFun
from utils.myexcept import TokenError
from utils.push import privatePush, sendEmail
from utils.utils import openJson, writeJson, timeRange
from library.consts import PATH_PAIR1


def exceptControl(user)->dict:
    """ 流程控制、异常处理
    在函数 funControl(user) 的基础上增加异常处理
    """
 
    info_jar = {}                # msg_jar  程序运行信息包 
    for i in range(5): 

        try:                    # 如果正常的话就正常运行
            info_jar = reserveFun(user)
            return info_jar

        except TokenError as e: # Token 无效，终止程序
            info_jar['except'] += f"\n用户令牌错误，程序退出：{e}"
            return  info_jar

        except Exception as e:  # 网络不稳定时，需重新连接
            if i >= 4: 
                info_jar['except'] += f"\n多次连接失败，程序退出：{e}"
                return info_jar

# def exceptControl(user)->dict:
#     info_jar = {}                 
#     info_jar = reserveFun(user)
#     return info_jar

class ResrveThread(Thread):
    """ 预约定制子线程"""
 
    def __init__(self, que:Queue, usr):
        super().__init__()
        self.que = que
        self.usr = usr

    def run(self):
        jars = exceptControl(self.usr)
        self.que.put(jars)  


class ReserveManager():
    """ 预约管理类，单例 """

    QUE = Queue()
    

    def __init__(self, uesrlist):
        self.userlist = uesrlist
        self.cookdicts = {}
        self.threads: List[Thread] = [] 
        self.info_list: List[dict] = [] #所有用户的信息
        self.logs = ""

        self.__start()


    def __start(self):
        """ 开始批量处理程序"""

        for usr in self.userlist:
            self.threads.append(ResrveThread(self.QUE, usr))

        # 循环开启所有子线程
        for t in self.threads: t.start()
        for t in self.threads: t.join()
 
        que_cnt = 0
        while True: 
            if not self.QUE.empty():

                info_jar = self.QUE.get()
                self.info_list.append(info_jar)
 
                que_cnt += 1

            if que_cnt==len(self.userlist): break


    def __del__(self):
        """ 程序结束时推送邮件信息 """

        self.pusnInfo()


    def __neatenLogs(self):

        for info_jar in self.info_list: 
            name  = info_jar.get('name'     )
            seat  = info_jar.get('seat_name')
            lib   = info_jar.get('lib_name' )
            statu = info_jar.get('status'   ) 
            logs  = info_jar.get('alllogs'  ) 
            excep = info_jar.get('except'   ) 
            title = f"🧊 用户：{name}（{lib}{seat}号，{statu}）"
            if excep==None:
                self.logs += f"{title}\n{logs}\n\n" 
            else: 
                self.logs += f"{title}\n{logs}\n{excep}\n\n" 


    def printLogs(self):
        """ 输出程序运行日志至控制台 """

        if self.logs=="": 
            self.__neatenLogs()

        print(self.logs)


    def pushLogs(self, receive, ontime=[7,0,0], title=None):
        """ 发送程序运行日志至邮箱 
            @receive: email.com
        """
        if self.logs=="": self.__neatenLogs()

        try:
            if ontime != None:
                isend = timeRange(ontime, 5)
                if not isend: return

            if title == None:
                title = " 🔵 程序预约日志"

            if receive == "wxpush":
                privatePush(receive, title, self.logs)
            else:
                sendEmail(receive, title, self.logs)

        except: pass


    def pusnInfo(self):
        """ 根据配置推送预约信息至各手机"""
        for jar in self.info_list:
            # 若推送标志位为0、邮件主题为空则不推送
            if not jar.get('ispush' ): break
            if not jar.get('subject'): break
            
            msg = jar['email'], jar['subject'], jar['content']

            if jar.get('wxpush'):
                privatePush(*msg)
            else:
                sendEmail(*msg)


    def postProcess(self, path_pair=PATH_PAIR1, cookdicts:dict=None):
        """ 后处理，是否更新云盘 cookies 文件 """
        for info_jar in self.info_list:
            cook_jar = info_jar['cook_jar']
            if cook_jar: 
                self.cookdicts |= cook_jar

        # 云端及本地是否过期，若过期则写入服务器最新 cookies
        if cookdicts==None:
            cookdicts = self.cookdicts
        try:
            latestlst = list(cookdicts.keys())
            latestset = set(latestlst)

            localdict = openJson(path_pair[0])
            localist  = list(localdict.keys())
            localset  = set(localist)

            # set 正反比较
            dff1 = latestset.difference(set(localset)) 
            dff2 = localset.difference(set(latestset))  
            diff = len(dff1) + len(dff2)
            localexp = localdict[localist[0]]['EXPIRE']
            isexpire = localexp < int(time.time())
        except:
            isexpire = True
            diff = True

        # 如果数据变化、数据过期则上传新文件
        if isexpire or diff:
            w = Thread(target=writeJson, args=(path_pair, cookdicts)) 
            w.start()
            w.join()
 
