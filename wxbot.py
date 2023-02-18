import os
from WeChatPYAPI import WeChatPYApi
import urllib.parse
import time
import logging
from queue import Queue
import autoit
import requests
from flask import Flask, request
import threading

# 当前目录路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# https://github.com/mrsanshui/WeChatPYAPI

logging.basicConfig(level=logging.INFO)  # 日志器
msg_queue = Queue()  # 消息队列


def on_message(msg):
    """消息回调，建议异步处理，防止阻塞"""
    print(msg)
    msg_queue.put(msg)

wechat_exit = False
def on_exit(wx_id):
    """退出事件回调"""
    global wechat_exit
    wechat_exit = True
    print("已退出：{}".format(wx_id))


class WechatBot:
    def __init__(self) -> None:
        self.w = WeChatPYApi(msg_callback=on_message, exit_callback=on_exit, logger=logging)
        self.wx_id = ''


    def start(self):
        # 初次使用需要pip安装三个库：
        # pip install requests
        # pip install pycryptodomex
        # pip install psutil
        
        self.w.start_wx()
        time.sleep(2)
        relogin_wechat()
        while not self.w.get_self_info():
            time.sleep(5)
        my_info = self.w.get_self_info()
        self.wx_id = my_info["wx_id"]
        print("登陆成功！")
        print(my_info)

        # 拉取群列表
        lists = self.w.pull_list(self_wx=self.wx_id, pull_type=2)
        print(lists)

        # 发送文本消息
        #self.w.send_text(self_wx=self.wx_id, to_wx="19060057279@chatroom", msg='测试')
        #time.sleep(1)

        # 处理消息回调
        #while True:
        #    msg = msg_queue.get()
        #    print(msg)
        #    time.sleep(2)


bot = WechatBot()
app = Flask(__name__)

@app.route('/wechat/send/card/', methods=['GET'])
def wechatListenMsgCard():
    target = request.args.get('target', None)
    title = request.args.get('title', None)
    desc = request.args.get('desc', None)
    target_url = request.args.get('target_url', None)
    img_url = request.args.get('img_url', None)
    bot.w.send_card_link(
        self_wx=bot.wx_id,
        to_wx=target,
        title=title,
        desc=desc,
        target_url=target_url,
        img_url=img_url
    )
    return 'Hello World! Card, ' + target


@app.route('/wechat/send/', methods=['GET'])
def wechatListenMsg():
    target = request.args.get('target', None)
    msg = request.args.get('msg', None)
    bot.w.send_text(self_wx=bot.wx_id, to_wx=target, msg=msg)
    return 'Hello World! ' + target

@app.route('/wechat/send/default/', methods=['GET'])
def wechatListenMsgDefault():
    msg = request.args.get('msg', None)
    bot.w.send_text(self_wx=bot.wx_id, to_wx="19060057279@chatroom", msg=msg)
    return 'Hello World! 19060057279@chatroom!'

@app.route('/wechat/send/filehelper/', methods=['GET'])
def wechatListenMsgFilehelper():
    msg = request.args.get('msg', None)
    bot.w.send_text(self_wx=bot.wx_id, to_wx="filehelper", msg=msg)
    return 'Hello World! filehelper'



def relogin_wechat():
    wx_handle = "[CLASS:WeChatLoginWndForPC]"
    try:
        autoit.win_activate(wx_handle)
        print('>> 需要登录微信')
        time.sleep(1)
        autoit.control_click(wx_handle, "")
        autoit.control_send(wx_handle, "", "{TAB 2}")
        autoit.control_send(wx_handle, "", "{Enter}")
        requests.get('http://xfxuezhang.cn:9966/QQ/send/friend?target=1061700625&msg=哗啦啦小助手需要重新登录微信了')
        try:
            autoit.win_wait("[CLASS:WeChatMainWndForPC]", 60)
            print('>> 微信已经登录')
            return True
        except:
            print('>> 微信登录超时')
            return False
    except:
        print('>> 没有微信登录登录界面')
    try:
        autoit.win_wait("[CLASS:WeChatMainWndForPC]", 5)
        print('>> 微信已经登录')
        return True
    except:
        print('>> 微信不存在')
    return False


if __name__ == '__main__':
    t = threading.Thread(target=app.run, args=('0.0.0.0', '9967'))
    t.setDaemon(True)
    t.start()
    bot.start()
    print('>> 启动成功')
    # while True:
    #     try:
    #         bot.start()
    #         print('>> 启动成功')
    #         while True:
    #             if wechat_exit:
    #                 print('>> 微信异常退出')
    #                 wechat_exit = False
    #                 #bot.logout(bot.wx_id)
    #                 break
    #             time.sleep(10)
    #     except:
    #         print('>> 报错重开')
    #     time.sleep(1)


