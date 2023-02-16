from email.mime.multipart import MIMEMultipart
from config.config import user, passwd, servchan
from email.mime.text import MIMEText
from email.utils import formataddr  
from utils.weather import weather  
import requests
import smtplib
import time


def sendEmail(email, subject, content):

    try:
        msg = MIMEMultipart() 
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        msg['From'   ] = formataddr(["预约机器人", user])
        msg['to'     ] = email
        msg['Subject'] = subject

        smtpser = smtplib.SMTP_SSL("smtp.qq.com", 465)
        smtpser.login(user, passwd)
        smtpser.sendmail(user, email, msg.as_string())
        smtpser.quit()

    except Exception as e:
        print(f'🟠 邮件 {email} 发送失败：{e}' )


def privatePush(email, subject, content):
    """ 紧急推送微信消息至手机 """
 
    url  = f"https://sctapi.ftqq.com/{servchan}.send"
    data = {'text': subject, 'desp': content}
    requests.post(url, data=data)


def weatherinfo()->str:
    """ 获取今日天气信息 """
    dates = time.strftime("%y-%m-%d", time.localtime())
    hours = int(time.strftime("%H", time.localtime()))
    skycon, description, temperature, probability = weather()

    if hours>0 and hours<11:
        greet = "早上好"
    elif hours>=11 and hours<18:
        greet = "下午好"
    else:
        greet = "晚上好"

    greet = f"{greet}，今天是 {dates}"

    descrip1 = f"天气：{description}"
    descrip2 = f"温度：{temperature}，未来半小时降雨量：{probability} mm/h"

    return f"{greet}\n{descrip1}\n{descrip2}"