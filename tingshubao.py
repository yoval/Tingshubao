# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 00:44:02 2022

@author: fuwen
"""
import requests,re,json,time

#书籍链接
book_url = 'http://m.tingshubao.com/book/3215.html'
#输出目录
outfloder = r'C:\Users\fuwen\Desktop\庆余年'
#下载方式
DownloadType = 0 # 0 python下载，1 调用Aria2 下载
#起始
strat = 1
end = 1000
#通过书籍链接获得播放链接
def get_book_list(book_url):
    resp = requests.get(book_url,headers = headers)
    resp.encoding = 'gb2312'
    html = resp.text
    book_name = re.findall('<title>(.*?)有声小说 - 演播', html)[0]
    url_list = re.findall("'第.*?集' href='.*?html'", html)
    url_list = ['http://m.tingshubao.com'+i.split("'")[3] for i in url_list]#播放页面列表
    return book_name,url_list

#通过播放链接获得下载链接
def get_download_url(audio_play_url):
    audio_play_response = requests.get(audio_play_url,headers = headers)
    audio_play_response.encoding = 'gb2312'
    autdio_play_html = audio_play_response.text
    encrypt_string = re.findall("FonHen_JieMa\('(.*?)'",autdio_play_html)[0]
    temp_list = []
    for temp in encrypt_string.split("*")[1:]:
        temp = chr(int(temp) & 0xffff)
        temp_list.append(temp)
    end_url = "".join(temp_list).split("&")[0]
    audio_detail_url = "http://43.129.176.64/player/key.php?url="
    audio_api_url = audio_detail_url + end_url
    audio_down_url = requests.get(audio_api_url).json()['url']
    return audio_down_url

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
    res = requests.get(download_url,headers = headers).content
    print('正在下载：%s'%FileName)
    with open(outfloder+'\\'+FileName, 'wb') as f:
        f.write(res)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29'}
book_name,url_list = get_book_list(book_url)
if len(url_list) >end:
    url_list = url_list[strat-1:end]
else:
    url_list = url_list[strat-1:]
for audio_play_url in url_list:
    download_url = get_download_url(audio_play_url)
    audio_name = re.findall('/(.*?)\?', download_url)[0]
    audio_name = audio_name.split('/')[-1]
    audio_name = book_name+'_'+audio_name
    time.sleep(5)
    if DownloadType ==1:
        Air2DownLoad(download_url,audio_name)
    elif DownloadType ==0:
        PythonDownLoad(download_url,audio_name)
    else:
        print('下载方式配置错误！')

