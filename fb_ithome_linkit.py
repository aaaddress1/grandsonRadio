#coding=utf-8
#!/usr/bin/python
import  threading, time
import requests
import json
from gtts import gTTS
import os
import re
import signal
import subprocess
import json

afplay = None
stop_play = False
activeReadPost = False
dont_kill = False
def getPIN13():
    gpio_path = '/sys/class/gpio/gpio0/value'
    ro = open(gpio_path, 'r')
    while True:
        try:
            return int(ro.read())
            ro.close()
        except ValueError:
            pass

def getButtonValue():
    gpio0 = getPIN13()
    time.sleep(0.2)
    gpio1 = getPIN13()
    time.sleep(0.2)
    gpio2 = getPIN13()
    true_gpio = 0
    if gpio1 == 1 and gpio0 == 1 and gpio2 == 1:
        true_gpio = 1
    return true_gpio

def ui_interface():
    global dont_kill
    global afplay
    global stop_play
    global activeReadPost
    print 'UI thread running successed!'
    while True:

        if getButtonValue() == 1:
            print 'button event'
            if not activeReadPost:
                activeReadPost = True
            else:
                if dont_kill:
                    pass
                else:
                    try:
                        afplay.kill()
                    except:
                        pass
                    print 'kill'
                    stop_play = True

        time.sleep(0.1)
    return

def playSound(max_index):
    global afplay
    global stop_play

    for i in range(max_index + 1):
        if stop_play:
            stop_play = False
            break
        if not afplay or afplay.poll() != None:
            afplay = subprocess.Popen([ 'madplay', '-S' ,'sound%d.mp3' % i ])
            afplay.wait()
    return

def say(context):
    context = unicode(context, 'utf-8')
    context = re.sub(ur'[～！＠＃＄％＾＆＊（）＿、｜＋\＼｜「『【〖」』】〗““"〃？／÷。⋯⋯》〉，《〈　~﹋"]', '', context)
    context = re.sub(ur'[：:]', u'說', context)
    tmp_buff = ''
    lastCharChinese = True
    index = 0

    for i in context:
        if ord(i) < 0x20:
            pass
        elif ord(i) <= 0x7e: #english

            if lastCharChinese and tmp_buff != '':
                print '-- 第 %d 句 -- ' % index
                print tmp_buff.encode('utf-8')
                tts = gTTS(text = tmp_buff.encode('utf-8'), lang = 'zh-tw')
                tts.save('sound%d.mp3' % index)
                index = index + 1
                tmp_buff = ''

            lastCharChinese = False
            if ord(i) in range(ord('A'), ord('Z') + 1):
                tmp_buff = tmp_buff + i
            if ord(i) in range(ord('a'), ord('z') + 1):
                tmp_buff = tmp_buff + i
            if ord(i) in range(ord('0'), ord('9') + 1):
                tmp_buff = tmp_buff + i
            if i == ' ':
                tmp_buff = tmp_buff + i

        else: #chinese

            if not lastCharChinese and tmp_buff != '':
                print '-- 第 %d 句 -- ' % index
                print tmp_buff.encode('utf-8')
                tts = gTTS(text = tmp_buff.encode('utf-8'), lang = 'zh-tw')
                tts.save('sound%d.mp3' % index)
                index = index + 1
                tmp_buff = ''
            
            lastCharChinese = True
            tmp_buff = tmp_buff + i

    if tmp_buff != '':
        print tmp_buff.encode('utf-8')
        tts = gTTS(text = tmp_buff.encode('utf-8'), lang = 'zh-tw')
        tts.save('sound%d.mp3' % index)

    playSound(index)
    return

def read_current_facebook_to_speech():

    # import facebook graph API & profile info
    with open('profile.json', 'r') as f:
        profile = json.load(f)
    reqUrl = '%s&oauth_token=%s' %  (profile['graphURL'] + profile['graphPath'], profile['usrAccessToken'])
    src = requests.get(reqUrl).text
    data = json.loads(src)
    
    count = 0
    for i in data['data']:
        if not 'message' in i:
            continue
        elif i['type'] == 'link':
            say('%s 分享了 %s 的內容，並留言說 %s' % (profile['shareTarget'].encode('utf-8'), i['name'].encode('utf-8'), i['message'].encode('utf-8')))
        elif i['type'] == 'photo':
            say('%s上傳了一張照片，並說%s' % (profile['shareTarget'].encode('utf-8'), i['message'].encode('utf-8')))
        elif i['type'] == 'status':
            say('%s發文說%s' % (profile['shareTarget'].encode('utf-8'), i['message'].encode('utf-8')))
        elif i['type'] == 'video':
            say('%s上傳了影片，並說%s' % (profile['shareTarget'].encode('utf-8'), i['message'].encode('utf-8')))
        
        count = count + 1
        if count >= 5:
            break

if __name__ == "__main__":
    # os.system("echo '0' > /sys/class/gpio/export")

    # for user, click button to shutdown current post speech 
    threading.Thread(target = ui_interface, args = (), name = 'ui_thread').start() 
    
    dont_kill = True
    say('孫子廣播電台已啟動')
    dont_kill = False
    # loop: waiting for user clicking button, and read post on facebook
    while True:
        
        if activeReadPost:
            dont_kill = True
            say('開始閱讀親朋好友在網路上的五四三')
            dont_kill = False
            read_current_facebook_to_speech()
            activeReadPost = False
            dont_kill = True
            say('感謝您收聽孫子廣播電台')
            dont_kill = False

        time.sleep(0.5)