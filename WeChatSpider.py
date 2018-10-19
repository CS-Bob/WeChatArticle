# encoding: utf-8
'''
@author: bo

@file: WeChatSpider.py
@time: 2018/10/10/010 15:02
@desc:
'''
import json
import re
import pymongo
import requests
from selenium import webdriver
from pyquery import PyQuery as pq
from urllib.parse import urlencode
from requests_html import HTMLSession
from selenium.webdriver.chrome.options import Options
from config import *

session = HTMLSession()
headers = {
    'Cookie': 'ABTEST=0|1539091980|v1; SUID=BE9AEC782423910A000000005BBCAE0C; SUID=BE9AEC784F18910A000000005BBCAE0C; weixinIndexVisited=1; SNUID=57730592E9EF9D222DC66678EAB316BC; JSESSIONID=aaaBEIMWSxqDa_6_6gszw; SUV=00881DEF78EC9ABE5BBCAE139A438848; IPLOC=CN4401; sct=3',
    'Host': 'weixin.sogou.com',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
}
client = pymongo.MongoClient(MONGO_URL) #连接本地mongo数据库
db = client[MONGO_DB]

# 1通过关键词获取it之家的url
def get_url(keyword):
    try:
        base_url = 'https://weixin.sogou.com/weixin?'  # 微信文章链接
        data = {
            'query': keyword,
            'type': '1',
        }
        data = urlencode(data)
        url = base_url + data  # 得到一系列名为it之家的公众号的页面的url
        r = session.get(url)
        my_url = r.html.find('#sogou_vr_11002301_box_0 > div > div.txt-box > p.tit > a')  # 获取我们所需要查询的目标公众号的链接的位置
        str1 = str(my_url)
        res = re.compile('.*?href=\'(.*?)\'.*?', re.S)
        resurl = re.findall(res, str1)
        url = "".join(resurl)
        return url  # 返回it之家的url
    except:
        return None

# 2.解析页面得到页面it之家所有文章的url
def get_article_url(url):
    try:
        print('正在爬取文章信息...请耐心等待')
        options = Options()  # 使用Chrome的headless模式，可以不用启动浏览器
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        # driver = webdriver.Chrome()
        driver.get(url)
        dates = []  # 日期的列表，暂时存储文章日期
        links = []  # url的列表，暂时存储文章url
        for date in driver.find_elements_by_class_name('weui_media_extra_info'):  # 获取文章的发布日期，由于文章内部的日期格式都为
            dates.append(date.text)  # 昨天，前天，三天前，诸如此类格式，所以，我选择
            # 在文章列表的外部抓取日期
        for link in driver.find_elements_by_class_name('weui_media_title'):  # 获取文章链接，这里文章链接缺少一部分
            links.append("https://mp.weixin.qq.com" + (link.get_attribute("hrefs")))  # 故使用字符串连接的方式来获取链接

        pre_links = dict(zip(links, dates))  # 把文章的链接和日期对应生成一个字典并返回
        return pre_links
    except:
        return None

# 3.得到文章的数据信息
def get_article_data(links):
    for url in links.keys():          #字典的key保存着url，url相对应的日期保存在value中
        # print(url)
        response = requests.get(url)
        article_html = response.text
        doc = pq(article_html)
        date = convert(links[url])     #将获取的日期格式化
        content = doc('.rich_media_content').text()                                       #文章内容
        total = db['ithome'].count()                                                      #当前数据库中总共数据量
        id = total+1                                                                      #id
        # precontent = content.replace('\n','')
        article_data = {
            'title': doc('#img-content .rich_media_title').text(),                        #标题
            'date': date,                                                                 #日期
            '_id': id,                                                                     #id
            'content': content,                                                            #内容
            'url': url,                                                                    # 链接
        }
        print(article_data)
        # print(article_data['title'])
        # list_title = get_mongo_titles()
        if article_data_exist(article_data):                                                   #检验数据库中是否已经存入该数据
            print('文章已存在数据库中，无需保存至数据库')                                      #存在则不需要保存至数据库
        else:                                                                                  #否则，保存到数据库内
            write_to_file(article_data)                                                        #保存到文件
            save_to_mongo(article_data)                                                        #保存到mongodb数据库

# 4.写入文件
def write_to_file(content):                                     #把获取到的每部文章的信息存入article.txt当中，一行存储一篇文章的信息
    with open('article.txt','a', encoding='utf-8') as f:
        f.write(json.dumps(content,ensure_ascii=False) + '\n')
        f.close()
# 5.保存到数据库当中
def save_to_mongo(article_data):
    try:
        if db[MONGO_TABLE].insert_one(article_data):                #插入到数据库当中
            print('成功存储到数据库')
    except Exception:
        print('存储到数据库失败',article_data)

#6.根据传入的文章信息 比较查看数据库中已经存在该文章
def article_data_exist(article_data):
    list_title = db[MONGO_TABLE].distinct('title')
    for list in list_title:
        if article_data['title'] == list:
            return True
    return False

#日期转换函数 如把2018年9月8日转换为2018-09-08
def convert(str):
    lis = re.findall('(\d+)', str)
    date = '%s-%s-%s' % (lis[0], lis[1].zfill(2), lis[2].zfill(2))
    return date

def Spider():
    url = get_url(KEYWORD)  # 获取it之家公众号的文章列表
    links = get_article_url(url)  # 得到所有文章的url
    get_article_data(links)  # 得到文章的所有信息，并且写入文件，保存到数据库

if __name__ == '__main__':
    Spider()
