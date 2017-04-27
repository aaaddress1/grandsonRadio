#coding=utf-8
from gtts import gTTS
import os

def data_generator():
    with open('testfile', 'r') as f:
        return f.read()

def say(context):
    context = unicode(context, 'utf-8')
    tmp_buff = ''
    if ord(context[0]) <= 0x7e: lastCharChinese = False
    else: lastCharChinese = True
    index = 0


    for i in context:
        if ord(i) < 0x20:
            if i == '\n':
                tmp_buff = tmp_buff + ' '

        elif ord(i) <= 0x7e: #english

            if lastCharChinese:
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

            if not lastCharChinese:
                print '-- 第 %d 句 -- ' % index
                print tmp_buff.encode('utf-8')
                tts = gTTS(text = tmp_buff.encode('utf-8'), lang = 'zh-tw')
                tts.save('sound%d.mp3' % index)
                index = index + 1
                tmp_buff = ''
                lastCharChinese = True
            tmp_buff = tmp_buff + i
    if tmp_buff != '':
        print tmp_buff
        tts = gTTS(text = tmp_buff.encode('utf-8'), lang = 'zh-tw')
        tts.save('sound%d.mp3' % index)

    for i in range(index + 1):
        os.system('madplay -S sound%d.mp3' % i)

say(data_generator())
