from utils.utils import TimerThread, openJson, timeRange, isOverTime
from library.consts import Operate, LOCAL_PATH 
from utils.myexcept import TokenError
from utils.loginfo import LogInfo
import requests
import json
import time
import re
requests.packages.urllib3.disable_warnings() 
 

class SeatSystem():
    """ 图书馆座位预约系统 """
  
    def __init__(self, USER):
        self.isresrved   = False    # 是否预约座位 
        self.often_seats = []       # 常用座位列表
        self.currentuser = {}       # 当前用户信息
        self.reserveinfo = {}       # 座位预约信息
        self.stoken      = None     # 自己退座令牌
        self.lib_id      = None     # 阅览室的 ID
        self.lib_name    = None     # 阅览室的名称
        self.seat_key    = None     # 座位的坐标
        self.seat_name   = None     # 座位的号码
        self.status      = 0        # 自己座位状态
        self.diff_str    = 0        # 本在馆学习时长
        self.exp_date    = 0        # 签到的过期时间
        self.cookdict    = {}       # 获取的cookies
        self.cook_jar    = {}       # 封装cookies包
        self.loacal_jar  = {}       # 本地cookies包

        # 初始化用户的数据信息
        self.Name   = USER['name']
        self.Email  = USER['email']
        self.Token  = USER['token']
        self.SeatID = USER['seat_prefer']

        # 记录运行日志，可发送邮件
        self.logs = LogInfo(self.Email, self.Name)
        self.logs.putInfo("创建对象，开始运行")
        self.cookdict = self.loadCookies()
        self.updateReserveInfo()
    

    def __del__(self):
        """ 销毁时后处理函数 """
        self.signTask()
        self.logs.putInfo("执行完毕，结束运行")


    def loadCookies(self):
        """ 从文件中读取并返回 Cookies """
 
        try: 
            self.loacal_jar  = openJson(LOCAL_PATH)
            data = self.loacal_jar[self.Name]

            # 如果读取的 cookies 未过期，则赋给成员变量
            if int(time.time()) < data['EXPIRE' ]:
                self.cookdict   = data['COOKIES']
                self.logs.putInfo("已获取本地获取数据")
                self.cook_jar = {
                    self.Name: self.loacal_jar[self.Name]
                }
            else: raise Exception("本地 cookies 过期")

        except Exception as e: 
            # 如果 cookies 文件不存在，则写入
            # self.logs.putLog(f"问题：{e}")
            self.logs.putInfo("正在从服务器获取数据...")
            self.cookdict = self.gainCookie()

        return self.cookdict
 

    def gainCookie(self):
        """ 获取 Cookies 并写入文件，有效期 1h """
        paraurl = "https://wechat.v2.traceint.com/index.php/reserve/index.html?f=wechat"
        authUrl = f"http://wechat.v2.traceint.com/index.php/urlNew/flagSeat?token={self.Token}"
        athHead = Operate.athHead.value
        
        session = requests.session()
        session.keep_alive = False

        session.post(paraurl, headers=athHead ,verify=False)
        cookdict1 = requests.utils.dict_from_cookiejar(session.cookies)

        session.post(authUrl, headers=athHead ,verify=False)
        cookdict2 = requests.utils.dict_from_cookiejar(session.cookies)

        self.cookdict = cookdict1 | cookdict2

        # 检查是否获取到授权码 Authorization，若没有则需要终止程序
        if 'Authorization' not in self.cookdict:
            info = "💥 致命错误：图书馆预约失败，请配置有效的 Token"
            self.logs.setSubject(info)
            raise TokenError(info)
        else: self.logs.putInfo("服务器数据获取成功")

        # 将有效时间，以及 获取的 cookies、授权码 存入文件
        self.cook_jar = {
            self.Name: {
                '获取时间': time.strftime("%H:%M:%S", time.localtime()),
                'EXPIRE':  int(time.time()) + 3600,
                "COOKIES": self.cookdict
            }
        }
        return self.cookdict


    def updateServerTime(self):
        """ 更新请求 SERVERID 的时间 """

        timestr = f"|{int(time.time())}|"
        try:
            self.cookdict['SERVERID'] = re.sub("\\|.*?\\|", timestr, self.cookdict['SERVERID'])
        except Exception as e:
            self.logs.putInfo(f"SERVERID 更新错误：{e}")
            self.gainCookie()


    def postOperation(self, operate: Operate):
        """ 操作请求模板 """
        url = "http://wechat.v2.traceint.com/index.php/graphql/"

        try: self.cookdict['Authorization']
        except: self.gainCookie()

        self.updateServerTime()  # 更新 SERVERID 时间
        head = Operate.pstHead.value
        resp = requests.post(url, json=operate.value, headers=head, cookies=self.cookdict, verify=False)
        resp = json.loads(resp.text)

        return resp


    def signTask(self):
        """ 每日签到获取积分 """ 
        try:
            self.updateReserveInfo()
            resp = self.postOperation(Operate.getList)
            task_id = resp['data']['userAuth']['credit']['tasks'][0]['id']

            task = Operate.doneTask
            task.value['variables']['user_task_id'] = task_id

            resp = self.postOperation(task)
            done = resp['data']['userAuth']['credit']['done']

            if done: self.logs.putInfo("签到成功，已获取 5 积分")
            # else: self.logs.log("今日已签到，明天再来吧")
        except Exception as e:
            self.logs.putInfo(f"签到错误：{e}")


    def updateReserveInfo(self):
        """ 查询座位相关信息，并保存至日志工具中 """

        # self.postOperation(Operate.getUserCancleConfig)
        info = self.postOperation(Operate.index)
        # 如果无法通过认证则重新获取授权码
        if 'errors' in info and info['errors'][0]['code'] == 40001:
            self.logs.putInfo("临时授权码过期，正在重新获取...")
            self.gainCookie()

        try:
            self.currentuser = info['data']['userAuth']['currentUser']     # 用户信息
            self.often_seats = info['data']['userAuth']['oftenseat']['list'] # 常用座位
            self.reserveinfo = info['data']['userAuth']['reserve']['reserve'  ] # 预约信息
            self.stoken      = info['data']['userAuth']['reserve']['getSToken'] # 退座令牌
            self.lib_id      = self.reserveinfo['lib_id'   ]                    # 场馆 ID
            self.lib_name    = self.reserveinfo['lib_name' ]                    # 场馆名称
            self.seat_key    = self.reserveinfo['seat_key' ]                    # 座位 ID
            self.seat_name   = self.reserveinfo['seat_name']                    # 座位号码
            self.status      = self.reserveinfo['status'   ]                    # 座位状态
            self.exp_date    = self.reserveinfo['exp_date' ]                    # 过期时间
            self.diff_str    = self.reserveinfo['diff_str' ]                    # 在馆时长
            self.isresrved   = True         # 若 userAuth.reserve 信息均正确则说明已经预约座位
        except Exception as e:
            # self.logs.putLog(f"当前无预约信息：{e}")
            self.isresrved = False

        #更新信息后将信息收集到 jar 包中
        status = ["未预约", "未预约", "待签到", "在馆", "暂离"]
        info_jar = {
            # "name":     self.currentuser.get("user_student_name"),
            "name":     self.Name,
            "email":    self.Email,
            "lib_name": self.lib_name,
            "seat_name":self.seat_name,
            "status":   status[self.status],
            "diff_str": self.diff_str,
            "cook_jar": self.cook_jar
        }
        self.logs.setSeatInfo(info_jar)

        return info_jar
 

    def reserveSeat(self, goalseat=None):
        """ 预约常用座位，默认预约常用座位
            theseat=[lib_id, seat_key]
        """
        self.updateReserveInfo()

        # 若未指定座位则选择常用座位
        if goalseat==None:
            isovertime = isOverTime([7, 1, 0])
            # 若常用座位不空闲，则切换另一常用座位 # 座位锁定：status=1
            oftenseat = self.often_seats[self.SeatID-1]
            if oftenseat['status']==1 and isovertime:  
                oftenseat = self.often_seats[2-self.SeatID] 

            lib_id    = oftenseat['lib_id'  ]
            seat_key  = oftenseat['seat_key']

        else:
            lib_id    = goalseat[0]
            seat_key  = goalseat[1]

        # 当前没有预约座位，则开始预约
        if (not self.isresrved):
            seat = Operate.reserveSeat
            seat.value['variables']['libId'  ] = lib_id
            seat.value['variables']['seatKey'] = seat_key 
            
            self.logs.putInfo(f"♻️ 开始预约：{seat_key}")
            resp = self.postOperation(seat)
 
            if 'errors' in resp:
                error = resp['errors'][0]['msg' ]
                ercod = resp['errors'][0]['code']
                self.logs.putInfo(f"预约失败：{error} [{ercod}]" )
                #错误码1:重复预约，错误码2:场馆关闭 
                self.logs.setSubject(f"🚫 图书馆预约失败：{error}")
                return False

            else:
                self.updateReserveInfo()
                lib_name, seat_name = self.lib_name, self.seat_name 
                self.logs.putInfo(f"预约成功：{lib_name} {seat_name}")
                self.logs.setSubject(f"🟢 图书馆预约成功：{lib_name} {seat_name}号")
                return True

        else: return True
 

    def cancelSeat(self):
        """ 主动退座 """

        self.updateReserveInfo()

        if (self.isresrved):
            cancel = Operate.reserveCancle
            cancel.value['variables']['sToken'] = self.stoken
            self.postOperation(cancel)
            self.updateReserveInfo()

            if not self.isresrved:
                self.isresrved = False
                self.logs.putInfo(f"退座成功，本次学习时长：{self.diff_str}")
                return True
            else:
                self.logs.putInfo("退座失败，未知错误")
                return False

        else: return True
 

    def reserveTimer(self, ontime=[7,0,0]):
        """ 早上 7 点准点预约，默认预约一号常用位 """

        self.updateReserveInfo()
        
        if not self.isresrved:
            sched = TimerThread()
            sched.addjob(ontime, self.reserveSeat)
            sched.addjob(ontime, self.reserveSeat)
            sched.addjob(ontime, self.reserveSeat)

 

    def reserveRenew(self, ontime:list):
        """ 若在指定时间前未签到，则重新预约 """

        self.updateReserveInfo()

        intime = timeRange(ontime, 5)
        renew  = self.status==2
        
        # status：未预约None，未签到2，在馆3，暂离4
        if intime and renew:
            self.cancelSeat()
            self.reserveSeat([self.lib_id, self.seat_key])

            self.updateReserveInfo()
            if (self.isresrved):
                self.logs.putInfo("预测当前无法签到，已自动续约")
                self.logs.setSubject("♻️ 图书馆预约超时，已自动续约")
            else:
                self.logs.setSubject("🍁 图书馆预约超时，续约失败了")


    def reserveCancel(self, ontime:list):
        """ 若指定时间前仍无法签到，则取消预约 """

        self.updateReserveInfo()
        
        intime = timeRange(ontime, 5)
        cancel = self.status==2
        
        # status：未预约None，未签到2，在馆3，暂离4
        if intime and cancel:
            # 若是系统全程自动续约，过期时间应该相差5min内
            if abs(time.time() - self.exp_date) < 300:
                self.cancelSeat()
                self.logs.putInfo("预测无法签到，故取消预约")
                self.logs.setSubject("🍁 图书馆预约再次超时，已取消预约")


    def closeCancel(self, ontime=[22,0,0]):
        """ 晚上 22点 闭馆 自动退座 """

        self.updateReserveInfo()

        intime = timeRange(ontime, 5)
        if intime and self.isresrved:
            self.cancelSeat()
            self.logs.setSubject("🍀 22点闭馆，已自动退座")


    def outTimeCancel(self):
        """ 预约超时前5分钟 自动退座 """

        self.updateReserveInfo()
        isTimeout  = self.exp_date - int(time.time()) < 5 * 60
        needCancel = self.status!=3 # 3为不在馆
 
        if self.isresrved and isTimeout and needCancel:
            self.reerveCancel()
            self.logs.putInfo("签到时间不足5分钟，已取消预约")
            self.logs.setSubject("🍁 图书馆座位超时，已自动取消")
            return True
        else:
            return False
