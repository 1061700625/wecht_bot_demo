# coding: utf-8


import requests
import time
import random
from apscheduler.schedulers.blocking import BlockingScheduler
import urllib.parse
import pyshorteners
import autoit


def relogin_wechat(autostart=False):
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
        if autostart:
            autoit.run(r'E:\Tencent\WeChat\WeChat.exe')
    return False


def sendDaily(msg, target='913182235'):
    print(msg)
    url = 'http://xfxuezhang.cn:9966/QQ/send/group?target={}&msg={}'.format(target, msg)
    requests.get(url)


def sendWechatCard(msg:map, target='19060057279@chatroom'):
    print(msg)
    print(msg)
    msg = urllib.parse.urlencode(msg)
    url = 'http://xfxuezhang.cn:9966/QQ/send/?target='+target + '&' + msg
    requests.get(url)


def sendDailyWechat(msg, target='19060057279@chatroom'):
    print(msg)
    msg = urllib.parse.quote(msg)
    url = 'http://127.0.0.1:9967/wechat/send/?target={}&msg={}'.format(target, msg)
    requests.get(url)

def common(data):
    key = 'e05966abe0b054686c9f6b7d60e59a8d'
    url = data + '?key={}'.format(key)
    res = requests.get(url).json()
    return res['newslist']


def getNews():
    # url = 'http://c.3g.163.com/nc/article/list/T1467284926140/0-20.html'
    res = common('http://api.tianapi.com/topnews/index')
    tops = []
    index = 1
    for item in res:
        tops.append(str(index) + '. ' + item['title'])
        index += 1
    return '\n'.join(tops[0:10])


def getYiQing():
    url = 'https://c.m.163.com/ug/api/wuhan/app/data/list-total?t={}'.format(329091037164)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/96.0.4664.110 Safari/537.36 '
    }
    res = requests.get(url, headers=headers).json()
    total = res['data']['chinaTotal']['total']
    today = res['data']['chinaTotal']['today']
    a = 99
    symbol_today = '＋' if today['confirm'] >= 0 else ''
    symbol_total = '＋' if today['storeConfirm'] >= 0 else ''
    symbol_input = '＋' if today['input'] >= 0 else ''
    confirmTotal = '累计确诊：{}，较昨日：{}{}'.format(total['confirm'], symbol_today, today['confirm'])
    confirmToday = '现有确诊：{}，较昨日：{}{}'.format(total['confirm'] - total['dead'] - total['heal'], symbol_total, today['storeConfirm'])
    inputs = '境外输入：{}，较昨日：{}{}'.format(total['input'], symbol_input, today['input'])
    return inputs + '\n' + confirmToday + '\n' + confirmTotal


def getHistoryToday():
    url = 'https://api.oick.cn/lishi/api.php'
    res = requests.get(url).json()
    historyToday = []
    for item in res['result']:
        historyToday.append(item['date'] + ', ' + item['title'])
    return '\n'.join(random.choices(historyToday, k=3))


def healthTips():
    res = common('http://api.tianapi.com/healthtip/index')
    tipsArray = res[0]
    return tipsArray['content']


def dailyTips():
    res = common('http://api.tianapi.com/qiaomen/index')
    tipsArray = res[0]
    return tipsArray['content']


def dailysentence():
    url = 'https://res.abeim.cn/api-text_yiyan'
    res = requests.get(url).json()
    return res['content']


def start():
    tops = getNews()
    yiqing = getYiQing()
    HistoryToday = getHistoryToday()
    health = healthTips()
    daily = dailyTips()
    sentence = dailysentence()
    spoofing = antiSpoofingSimple()

    content = '''【早上好~】
▶ 今日头条：
{}

❤ 全国疫情数据(含港澳台)：
{}

✍ 历史上的今天：
{}

❤ 健康小贴士：
{}

✌ 生活小窍门：
{}

☺ 每日一句：
{}

☄ 反诈小贴士：
{}
'''.format(tops, yiqing, HistoryToday, health, daily, sentence, spoofing)

    #sendDaily(content)
    relogin_wechat()
    sendDailyWechat(content, target='7721144411@chatroom')
    #sendDailyWechat(content.strip(), target='filehelper')



antispoofing_store = []
def antiSpoofing():
    url = 'https://oss.gjfzpt.cn/preventfraud-static/h5/list/1-1/1-1-1.json'
    res = requests.get(url).json()
    lists = res['list']
    content = ''
    max_item = 3
    for item in lists[:max_item]:
        id = item['id']
        title = item['title']
        localFilePath = item['localFilePath']
        releaseTime = item['releaseTime']
        if id in antispoofing_store:
            continue
        else:
            if len(antispoofing_store) >= max_item: 
                antispoofing_store.pop(0)
            antispoofing_store.append(id)
            localFilePath = pyshorteners.Shortener().clckru.short(localFilePath)
            content += f'☠【{title}】——[{releaseTime}]\n☛{localFilePath}☚\n\n'
    #sendDailyWechat(content.strip(), target='7721144411@chatroom')
    return content.strip()

def antiSpoofingSimple(max_item=3):
    url = 'https://oss.gjfzpt.cn/preventfraud-static/h5/list/1-1/1-1-1.json'
    res = requests.get(url).json()
    lists = res['list']
    content = ''
    for item in lists[:max_item]:
        title = item['title']
        localFilePath = item['localFilePath']
        releaseTime = item['releaseTime']
        localFilePath = pyshorteners.Shortener().clckru.short(localFilePath)
        content += f'☠【{title}】——[{releaseTime}]\n☛{localFilePath}☚\n\n'
    #sendDailyWechat(content.strip(), target='7721144411@chatroom')
    return content.strip()


if __name__ == '__main__':
    print('开始运行...')
    #relogin_wechat()
    #exit()
    force_run = False
    if force_run and time.localtime().tm_hour>=9 and time.localtime().tm_min>=0:
        print('直接运行...')
        start()
    else:
        print('定时运行...')
        scheduler = BlockingScheduler()
        scheduler.add_job(start, 'cron', day_of_week='*', hour=9, minute='00', second='00', timezone='Asia/Shanghai')
        scheduler.start()








