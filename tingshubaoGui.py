# -*- coding: utf-8 -*-
"""
Created on Tue Apr  5 00:14:16 2022

@author: fuwen

喜马拉雅、懒人听书
"""
import requests,re,json,time
import PySimpleGUI as sg

import os
import sys
os.environ['REQUESTS_CA_BUNDLE'] =  os.path.join(os.path.dirname(sys.argv[0]), 'cacert.pem')
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29'}
sg.theme('GreenTan')
#通过书籍链接获得播放链接
def get_book_list(book_url):
    resp = requests.get(book_url,headers = headers)
    resp.encoding = 'gb2312'
    html = resp.text
    book_name = re.findall('<h1 class="book-title">(.*?)</h1>', html)[0]
    url_list = re.findall("'第.*?' href='.*?html'", html)
    url_list = ['http://m.tingshubao.com'+i.split("'")[3] for i in url_list]#播放页面列表
    return book_name,url_list

#通过播放链接获得下载链接
def get_download_url(audio_play_url):
    audio_play_response = requests.get(audio_play_url,headers = headers)
    audio_play_response.encoding = 'gb2312'
    audio_play_html = audio_play_response.text
    audio_name = re.findall(r"no: '(.*?)'", audio_play_html)[0]
    encrypt_string = re.findall("FonHen_JieMa\('(.*?)'",audio_play_html)[0]
    temp_list = []
    for temp in encrypt_string.split("*")[1:]:
        temp = chr(int(temp) & 0xffff)
        temp_list.append(temp)
    end_url = "".join(temp_list).split("&")[0]
    audio_detail_url = "http://43.129.176.64/player/key.php?url="
    audio_api_url = audio_detail_url + end_url
    audio_down_url = requests.get(audio_api_url).json()['url']
    if 'audio.xmcdn.com' in audio_down_url:
        print('喜马拉雅源……')
        audio_down_url = audio_down_url.replace('t3344t.tingchina.com/','')
    else:
        print('听中国源……')
    return audio_down_url,audio_name

#调用Air2下载
JsonRpcUrl = 'http://localhost:6800/jsonrpc'
def Air2DownLoad(DownloadUrl,FileName):
    PostData = {
        "jsonrpc":"2.0",
        "method":"aria2.addUri",
        "id":1,
        "params":[[DownloadUrl],
                  {"out":FileName,
                   "dir":outfloder,
                   "split":"32",
                   "max-connection-per-server":"5",
                   "seed-ratio":"0.1"}]}
    Send = requests.post(JsonRpcUrl,json.dumps(PostData))
    if Send.status_code==200:
        print('%s 推送成功！'%FileName)
    else:
        print('推送失败！请打开Aria2并确保正常运行。')
#调用Python下载
def PythonDownLoad(DownloadUrl,FileName):
    res = requests.get(DownloadUrl,headers = headers).content
    print('正在下载：%s'%FileName)
    with open(outfloder+'\\'+FileName, 'wb') as f:
        f.write(res)

frame3 = [[sg.Radio('内置下载器', "RADIO2", key = '-python-',size=(10, 1)),sg.Radio('Aria2', "RADIO2",key = '-aria2-',  size=(10, 1) ,default=True),sg.Text('RPC：'),sg.Input('http://localhost:6800/jsonrpc',key = '-RPC-',size=(50,1))],[sg.Text('书籍 ID：'),sg.Input('3215',key = '-bookid-',size=(8, 1)),sg.Text('开始：'),sg.Input('1',key = '-start-',size=(5, 1)),sg.Text('结束：'),sg.Input('10',key = '-end-',size=(5, 1)),sg.Text('间隔：'),sg.Input('5',key = '-jiange-',size=(5, 1))],]
layout = [
    [sg.Column([[sg.Frame('下载选项:', frame3,size=(480,80))]]),],
    [sg.Text('下载至目录：'),sg.Input(),sg.FolderBrowse('浏览',key = '-outfloder-')],
    [sg.Button('确认',key = 'ok')],
    [sg.Text('输出日志：')],
    [sg.Output(size=(70, 6))],
    ]
window = sg.Window('听书宝下载工具 v0.4', layout)
while True:
    event, values = window.Read()
    if event in (None, 'Cancel'):
        break
    outfloder = values['-outfloder-']
    RPC = values['-RPC-']
    book_id = values['-bookid-']
    DownloadType = values['-aria2-']
    strat = values['-start-']
    end = values['-end-']
    jiange = values['-jiange-']
    book_url = 'http://m.tingshubao.com/book/%s.html'%book_id
    count = int(strat)
    try:
        book_name,url_list = get_book_list(book_url)
    except:
        print('书籍信息获取失败！即将重试……')
        time.sleep(int(jiange))
        book_name,url_list = get_book_list(book_url)
    url_list=url_list[int(strat)-1:int(end)]
    for audio_play_url in url_list:
        download_url,audio_name = get_download_url(audio_play_url)
        houzui = download_url.split('.')[-1]#获取后缀
        houzui = houzui.split('?')[0]
        audio_name = book_name + '_' + audio_name+'.'+houzui
        if DownloadType ==True:
            Air2DownLoad(download_url,audio_name)
        else:
            PythonDownLoad(download_url,audio_name)
window.Close()