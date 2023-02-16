import datetime  
 

class LogInfo():
    """ 日志信息控制类 """
 

    def __init__(self, Email=None, Name=None):
        """ Email: 接收人的邮箱 """
        self.Name  = Name
        self.Email = Email 
        self.subject = None 
        self.info_jar  = {}     #信息包，对外暴露
        self.seatinfo  = {}     
        self.__infolst = []     #用于收集发送信息
        self.__logslst = []     #用于收集差错日志


    def getInfoJar(self):
        """ 返回字典形式的日志信息包 """

        content = '\n'.join(self.__infolst)
        alllogs = '\n'.join(self.__logslst) 
 
        # 在用户信息包的基础上增加日志信息 
        self.info_jar['subject'] = self.subject
        self.info_jar['content'] = content
        self.info_jar['alllogs'] = alllogs

        return self.info_jar


    def putInfo(self, info:str):
        """ 收集运行过程中的日志 """

        times = datetime.datetime.now().strftime('%H:%M:%S.%f')[:12]
        log_item = times + "  " + info
        self.__infolst.append(log_item)
        self.__logslst.append(log_item)
        

    def putLogs(self, info:str):
        """ 收集日志，非邮件发送用途"""
        times = datetime.datetime.now().strftime('%H:%M:%S.%f')[:12]
        log_item = times + "  " + info
        self.__logslst.append(log_item)


    def setSeatInfo(self, dicts:dict):
        """ 设置座位预约信息 """
        self.info_jar = dicts


    def setSubject(self, subject:str):
        """ 设置运行日志的标题 """
        self.subject = subject 
  
