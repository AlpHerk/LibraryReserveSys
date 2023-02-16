from enum import Enum
# 此文件用于存放程序的常量


# cookies 文件路径，磁盘根目录/tmp
LOCAL_PATH = "/tmp/cookies.json"
LOCAL_PATH2 = "/tmp/cookies2.json"
JIAN_PATH  = "/我去图书馆/cookies.json"
JIAN_PATH2 = "/我去图书馆/cookies2.json"
 
PATH_PAIR1 = [LOCAL_PATH , JIAN_PATH ]
PATH_PAIR2 = [LOCAL_PATH2, JIAN_PATH2]

# 场馆的座位状态 seat_status
# 个人的座位状态 status
# 无人(白色)  status=1
# 已选(绿色)  status=2 
# 有人(红色)  status=3 
# 暂离(灰色)  status=4 


class Operate(Enum):

    athHead = {
        "User-Agent":
        "Mozilla/5.0 (Linux; Android 11; Redmi K20 Pro Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/3171 MMWEBSDK/20220303 Mobile Safari/537.36 MMWEBID/7166 MicroMessenger/8.0.21.2103(0x28001541) Process/appbrand0 WeChat/arm64 Weixin GPVersion/1 NetType/4G Language/zh_CN ABI/arm64 MiniProgramEnv/android",
        "X-Requested-With": "com.tencent.mm",
        "Host": "wechat.v2.traceint.com",

    }
    pstHead = {
        "X-Requested-With": "com.tencent.mm",
        "User-Agent":
        "Mozilla/5.0 (Linux; Android 11; Redmi K20 Pro Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 XWEB/3171 MMWEBSDK/20220303 Mobile Safari/537.36 MMWEBID/7166 MicroMessenger/8.0.21.2103(0x28001541) Process/appbrand0 WeChat/arm64 Weixin GPVersion/1 NetType/4G Language/zh_CN ABI/arm64 MiniProgramEnv/android",
        "Content-Type": "application/json",
        "Referer": "http://web.traceint.com/web/index.html",
        "Origin": "http://web.traceint.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Connection": "keep-alive",
        "Host": "wechat.v2.traceint.com",
    }

    index = {
        "operationName": "index",
        "query":
        "query index($pos: String!, $param: [hash]) {\n userAuth {\n oftenseat {\n list {\n id\n info\n lib_id\n seat_key\n status\n }\n }\n message {\n new(from: \"system\") {\n has\n from_user\n title\n num\n }\n indexMsg {\n message_id\n title\n content\n isread\n isused\n from_user\n create_time\n }\n }\n reserve {\n reserve {\n token\n status\n user_id\n user_nick\n sch_name\n lib_id\n lib_name\n lib_floor\n seat_key\n seat_name\n date\n exp_date\n exp_date_str\n validate_date\n hold_date\n diff\n diff_str\n mark_source\n isRecordUser\n isChooseSeat\n isRecord\n mistakeNum\n openTime\n threshold\n daynum\n mistakeNum\n closeTime\n timerange\n forbidQrValid\n renewTimeNext\n forbidRenewTime\n forbidWechatCancle\n }\n getSToken\n }\n currentUser {\n user_id\n user_nick\n user_mobile\n user_sex\n user_sch_id\n user_sch\n user_last_login\n user_avatar(size: MIDDLE)\n user_adate\n user_student_no\n user_student_name\n area_name\n user_deny {\n deny_deadline\n }\n sch {\n sch_id\n sch_name\n activityUrl\n isShowCommon\n isBusy\n }\n }\n }\n ad(pos: $pos, param: $param) {\n name\n pic\n url\n }\n}",
        "variables": {
            "pos": "App-首页"
        }
    }

    getUserCancleConfig = {
        "operationName": "getUserCancleConfig",
        "query": "query getUserCancleConfig {\n userAuth {\n user {\n holdValidate: getSchConfig(fields: \"hold_validate\", extra: true)\n }\n }\n}",
        "variables": {}
    }

    reserveSeat = {
        "operationName": "reserveSeat",
        "query":
        "mutation reserveSeat($libId: Int!, $seatKey: String!, $captchaCode: String, $captcha: String!) {\n userAuth {\n reserve {\n reserveSeat(\n libId: $libId\n seatKey: $seatKey\n captchaCode: $captchaCode\n captcha: $captcha\n )\n }\n }\n}",
        "variables": {
            "seatKey": "",
            "libId": 122804,
            "captchaCode": "",
            "captcha": ""
        }
    }
    reserveCancle = {
        "operationName": "reserveCancle",
        "query":
        "mutation reserveCancle($sToken: String!) {\n userAuth {\n reserve {\n reserveCancle(sToken: $sToken) {\n timerange\n img\n hours\n mins\n per\n }\n }\n }\n}",
        "variables": {
            "sToken": ""
        }
    }
    getList = {
        "operationName":
        "getList",
        "query":
        "query getList {\n userAuth {\n credit {\n tasks {\n id\n task_id\n task_name\n task_info\n task_url\n credit_num\n contents\n conditions\n task_type\n status\n }\n staticTasks {\n id\n name\n task_type_name\n credit_num\n contents\n button\n }\n }\n }\n}"
    }
    doneTask = {
        "operationName": "done",
        "query":
        "mutation done($user_task_id: Int!) {\n userAuth {\n credit {\n done(user_task_id: $user_task_id)\n }\n }\n}",
        "variables": {
            "user_task_id": 0  # 需要补全参数 user_task_id
        }
    }
    user_credit = {
        "operationName":
        "user_credit",
        "query":
        "query user_credit {\n userAuth {\n currentUser {\n user_credit\n }\n }\n}"
    }
    libLayout = {
        "operationName": "libLayout",
        "query":
        "query libLayout($libId: Int, $libType: Int) {\n userAuth {\n reserve {\n libs(libType: $libType, libId: $libId) {\n lib_id\n is_open\n lib_floor\n lib_name\n lib_type\n lib_layout {\n seats_total\n seats_booking\n seats_used\n max_x\n max_y\n seats {\n x\n y\n key\n type\n name\n seat_status\n status\n }\n }\n }\n }\n }\n}",
        "variables": {
            "libId": 122804
        }
    }
