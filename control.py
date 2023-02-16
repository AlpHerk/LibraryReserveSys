from library.seatsys import SeatSystem
from utils.push import weatherinfo 
from config.config import * 
# 此文件是 manager 模块的依赖文件
# 为方便能修改预约功能，故提升至此
 

def reserveFun(user)->tuple[dict,dict,str]:
    """ 预约功能控制函数 """

    seat = SeatSystem(user) 
 
    # seat.reserveTimer([7, 0, 0])
    # seat.reserveRenew([8,29, 0])
    # seat.reserveCancel([8,58,0])
    # seat.closeCancel([22, 0, 0])
  
    seat.reserveSeat()  # 可试探预约处理

    seat.updateReserveInfo()

    info_jar = seat.logs.getInfoJar()    # 程序运行信息包
 
    if user['name'] == "USER_NAME1":
        info_jar['ispush' ] = False
        info_jar['wxpush' ] = False
        info_jar['content'] = f"{weatherinfo()}\n{info_jar['content']}"
  
    return info_jar

 