#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import codecs
import copy
import csv
import json
import math
import os
import random
import sys
import traceback
from collections import OrderedDict
from datetime import date, datetime, timedelta
from time import sleep
from bs4 import BeautifulSoup
import time
import requests
from lxml import etree
from requests.adapters import HTTPAdapter
from sqlalchemy.sql.functions import current_time
from tqdm import tqdm
import re
from bs4 import BeautifulSoup
import requests
from database_util import database_util
from config import *
from lxml import html
from html import unescape
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains

# 数据采集
class data_spider:
    def __init__(self):
        self.database = database_util()
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Referer': 'https://m.weibo.cn/',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
            'Cookie':'BIDUPSID=A21268228056FA3048029AC3B2C59256; PSTM=1720860095; BAIDUID=A21268228056FA304031695B25DCBAF7:FG=1; MCITY=-154%3A; BDUSS=1DOGRjNkFoQ21OVGFvYTJkUjF5Vmp3dS1jV1RKRUxxSG5keTNGaVM2VDhocUZuSVFBQUFBJCQAAAAAAAAAAAEAAAA24h3OTGlOaUFuMTYwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPz5eWf8-XlnTS; BDUSS_BFESS=1DOGRjNkFoQ21OVGFvYTJkUjF5Vmp3dS1jV1RKRUxxSG5keTNGaVM2VDhocUZuSVFBQUFBJCQAAAAAAAAAAAEAAAA24h3OTGlOaUFuMTYwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPz5eWf8-XlnTS; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; BAIDUID_BFESS=A21268228056FA304031695B25DCBAF7:FG=1; ZFY=k0RugYVvEqP1hyItWRkw6QQw:AXy5AqwB:AhaXd6xfyJs:C; H_WISE_SIDS_BFESS=61027_60853_61491_61530_61567_61609_61639_61722_61732; BDRCVFR[uPX25oyLwh6]=mk3SLVN4HKm; H_PS_PSSID=61027_60853_61491_61530_61567_61609_61639_61732; delPer=0; PSINO=3; BAIDU_WISE_UID=wapp_1736386180072_558; arialoadData=false; H_WISE_SIDS=61027_60853_61491_61530_61567_61609_61639_61732; ab_sr=1.0.1_MzFhODg1Zjk3MjVkZThmYTlhNmVhYjQxM2VkOTUzNjI0ZjM2ZjgzNWYxYzIwMDcxOGIwYTFmZjNiZGIyYWVhZDViYjRhNjRiNWE2MmJlNDQzNWQyNmQ3M2U5N2MzMjg0YTViYjI0OTljNmFiNjZkYzNkNzA3YzE1Zjk5MGJkNjg5N2M0YjNmNWIzNDBkYmFmYmE3ZTE1ZTUzN2MwYTEyODFiZGRlMzc3MTI1YmU3NDBkZWFmNzZlN2I2MmNkMzQz; RT="z=1&dm=baidu.com&si=3d9cf5e3-d763-459c-9d8e-0baa7a6d3f85&ss=m5onhzhw&sl=2e&tt=2c0y&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf"; BA_HECTOR=8h0h2ka58g24a4a5042h2525a4u6b41jnuf4v1v'
        }
        self.cookie = {'Cookie': weibo_config['cookie']}  # 微博cookie，可填可不填
        self.user = {}  # 存储目标微博用户信息
        self.got_count = 0  # 存储爬取到的微博数
        self.weibo = []  # 存储爬取到的所有微博信息
        self.weibo_id_list = []  # 存储爬取到的所有微博id
        self.comments = [] # 存储爬取到的所有评论
        self.mysql_config = weibo_config['mysql_config']
        # self.since_date = datetime.now().strftime('%Y-%m-%d')
        self.since_date = (datetime.today() - timedelta(730)).strftime('%Y-%m-%d')
        # chrome_driver = r"D:\_Application\Python\Python38\Lib\site-packages\selenium\webdriver\chrome\chromedriver.exe"
        # path = Service(chrome_driver)
        # self.driver = webdriver.Chrome(service=path)
        self.weibo_num = 1
        self.mysql_config = weibo_config['mysql_config']
        # self.since_date = datetime.now().strftime('%Y-%m-%d')
        self.since_date = (datetime.today() - timedelta(730)).strftime('%Y-%m-%d')
        self.con_id = '100103type=1&q=长沙理工大学'
        self.lfid_name = '100103type=61&q=长沙理工大学&t='
        self.since_id = None
        self.just_comment = True
    def start_spider(self):
        for item in spider_list:
            if(item == 'weibo'):
                self.spider_weibo()
    

     
    def GetMiddleStr(self,content,startStr,endStr):
        patternStr = r'%s(.+?)%s'%(startStr,endStr)
        p = re.compile(patternStr,re.IGNORECASE)
        m= re.match(p,content)
        if m:
            return m.group(1)

    # 时间转换
    def get_time_convert(self, timeStr):
        if (re.match('^\d{1,2}:\d{1,2}$', timeStr) != None):
            day = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            timeStr = day + ' ' + timeStr + ':00'
        elif (re.match('^\d{4}-\d{1,2}$', timeStr) != None):
            day = time.strftime('%d', time.localtime(time.time()))
            timeStr = timeStr + '-' + day + ' 00:00:00'
        elif (re.match('^\d{1,2}-\d{1,2}$', timeStr) != None):
            day = time.strftime('%Y', time.localtime(time.time()))
            timeStr = day + '-' + timeStr + ' 00:00:00'

        timeStr = time.strptime(timeStr, '%Y-%m-%d %H:%M:%S')

        return timeStr


    # 过滤表情
    def filter_emoji(self,desstr,restr=''):  
        try:  
            co = re.compile(u'[\U00010000-\U0010ffff]')  
        except re.error:  
            co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')  
        return co.sub(restr, desstr)

        
    def spider_weibo(self):
         # Step 1: 爬取最新的
        self.get_pages()
       # Step 2: 查询评论状态为未爬取的微博ID
        print("获取评论未爬取完成的微博...")
        unfinished_weibo_ids = self.database.get_unfinished_weibo()  # 查询 comments_fetched = 0 的微博
        if not unfinished_weibo_ids:
            print("所有微博的评论已爬取完成，无需继续爬取。")
            return

        # Step 3: 开始爬取未完成的微博评论
        print(f"开始爬取未完成评论的微博，共有 {len(unfinished_weibo_ids)} 条微博待处理。")
        self.weibo_id_list = unfinished_weibo_ids
        self.get_comments()  # 根据未完成的微博ID列表爬取评论

    def get_pages(self):
        """获取全部微博"""
        self.get_user_info()
        page_count = self.get_page_count()
        wrote_count = 0
        page1 = 0
        random_pages = random.randint(1, 5)
        self.start_date = datetime.now().strftime('%Y-%m-%d')
        for page in tqdm(range(1, page_count + 1), desc='Progress'):
            is_end = self.get_one_page(page)
            if is_end:
                break
            if page % 10 == 0:  # 每爬10页写入一次文件
                self.weibo_to_mysql(wrote_count)
                wrote_count = self.got_count
            # 通过加入随机等待避免被限制。爬虫速度过快容易被系统限制(一段时间后限
            # 制会自动解除)，加入随机等待模拟人的操作，可降低被系统限制的风险。默
            # 认是每爬取1到5页随机等待6到10秒，如果仍然被限，可适当增加sleep时间
            if (page - page1) % random_pages == 0 and page < page_count:
                sleep(random.randint(6, 10))
                page1 = page
                random_pages = random.randint(1, 5)

        self.weibo_to_mysql(wrote_count)  # 将剩余不足20页的微博写入文件
        print(u'微博爬取完成，共爬取%d条微博' % self.got_count)

    def get_user_info(self):
        """获取用户信息"""
        # params = {'containerid': '100505' + str(weibo_config['user_id'])}
        # params = {'containerid': self.con_id,
        #           'luicode': '10000011',
        #           'lfid': self.lfid_name,
        #           'since_id': self.since_id
        #           }
        params = { }


        js = self.get_json(params)

        if js['ok']:
            # print(js['data'])
            info = js['data']['userInfo']
            user_info = {}
            user_info['id'] = info.get('id', '')
            user_info['statuses_count'] = info.get('statuses_count', '')
            user_info['screen_name'] = info.get('screen_name', '')
            user_info['gender'] = info.get('gender', '')
            #user_info['statuses_count'] = info.get('total', 0)
            user_info['followers_count'] = info.get('followers_count', 0)
            user_info['follow_count'] = info.get('follow_count', 0)
            user_info['description'] = info.get('description', '')
            user_info['profile_url'] = info.get('profile_url', '')
            user_info['profile_image_url'] = info.get('profile_image_url', '')
            user_info['avatar_hd'] = info.get('avatar_hd', '')
            user_info['urank'] = info.get('urank', 0)
            user_info['mbrank'] = info.get('mbrank', 0)
            user_info['verified'] = info.get('verified', False)
            user_info['verified_type'] = info.get('verified_type', 0)
            user_info['verified_reason'] = info.get('verified_reason', '')
            user = self.standardize_info(user_info)
            self.user = user
        else:
            user_info = {}
            user_info['id'] = '1'
            user_info['screen_name'] = '全国高校'
            user_info['statuses_count'] = 1000
            user = self.standardize_info(user_info)
            self.user = user

    def standardize_info(self, weibo):
        """标准化信息，去除乱码"""
        for k, v in weibo.items():
            if 'bool' not in str(type(v)) and 'int' not in str(
                    type(v)) and 'list' not in str(
                type(v)) and 'long' not in str(type(v)):
                weibo[k] = v.replace(u"\u200b", "").encode(
                    sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
        return weibo

    def get_page_count(self):
        """获取微博页数"""
        try:
            weibo_count = self.user['statuses_count']
            page_count = int(math.ceil(weibo_count / 10.0))
            return min(80,page_count)
            # return 1000
        except KeyError:
            sys.exit(u'程序出错')

    def get_one_page(self, page):
        """获取一页的全部微博"""
        try:
            js = self.get_weibo_json(page)
            if js['ok']:
                # print(js['data']['cards'][0])
                weibos = js['data']['cards']
                # weibos = js['data']['cards'][0]['card_group']#超话用

                # print(weibos)

                for w in weibos:
                    if int(w['card_type']) == 11:
                        w = w['card_group'][0]
                    if int(w['card_type']) == 9:
                        wb = self.get_one_weibo(w)
                        try:
                            print(self.weibo_num, wb['text'])
                            self.weibo_num += 1
                        except:
                            pass
                        if wb:
                            # print(wb['id'])
                            # print(self.weibo_id_list)
                            if wb['id'] in self.weibo_id_list:
                                continue
                            wb['created_at'] = self.getTimeConvert(wb['created_at'])
                            since_date = datetime.strptime(
                                self.since_date, '%Y-%m-%d')
                            if wb['created_at'] < since_date:
                                if self.is_pinned_weibo(w):
                                    continue
                                else:
                                    print(u'{}已获取{}({})的第{}页微博{}'.format(
                                        '-' * 30, self.user['screen_name'],
                                        self.user['id'], page, '-' * 30))
                                    return True
                            if ('retweet' not in wb.keys()):
                                self.weibo.append(wb)
                                self.got_count += 1

            print(u'{}已获取{}({})的第{}页微博{}'.format('-' * 30,
                                                 self.user['screen_name'],
                                                 self.user['id'], page,
                                                 '-' * 30))
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def is_pinned_weibo(self, info):
        """判断微博是否为置顶微博"""
        weibo_info = info['mblog']
        title = weibo_info.get('title')
        if title and title.get('text') == u'置顶':
            return True
        else:
            return False

    def get_weibo_json(self, page):
        """获取网页中微博json数据"""
        # params = {
        #     'containerid': '107603' + str(weibo_config['user_id']),
        #     'page': page
        # }
        params = {'containerid': self.con_id,
                  'page_type': 'searchall',
                  'page': page
                  }
        js = self.get_json(params)
        try:
            self.since_id = js['data']['pageInfo']['since_id']
            # print(self.since_id)

        except:
            time.sleep(2)
        return js

    def get_json(self, params):
        """获取网页中json数据"""
        url = 'https://m.weibo.cn/api/container/getIndex?'
        r = requests.get(url, params=params, cookies=self.cookie)
        # print(r.url)
        return r.json()

    def get_one_weibo(self, info):
        """获取一条微博的全部信息"""
        try:
            weibo_info = info['mblog']
            weibo_id = weibo_info['id']
            retweeted_status = weibo_info.get('retweeted_status')
            is_long = weibo_info.get('isLongText')
            if retweeted_status:  # 转发
                retweet_id = retweeted_status.get('id')
                is_long_retweet = retweeted_status.get('isLongText')
                if is_long:
                    weibo = self.get_long_weibo(weibo_id)
                    if not weibo:
                        weibo = self.parse_weibo(weibo_info)
                else:
                    weibo = self.parse_weibo(weibo_info)
                if is_long_retweet:
                    retweet = self.get_long_weibo(retweet_id)
                    if not retweet:
                        retweet = self.parse_weibo(retweeted_status)
                else:
                    retweet = self.parse_weibo(retweeted_status)
                retweet['created_at'] = self.standardize_date(
                    retweeted_status['created_at'])
                weibo['retweet'] = retweet
            else:  # 原创
                if is_long:
                    weibo = self.get_long_weibo(weibo_id)
                    if not weibo:
                        weibo = self.parse_weibo(weibo_info)
                else:
                    weibo = self.parse_weibo(weibo_info)
            weibo['created_at'] = self.standardize_date(
                weibo_info['created_at'])
            return weibo
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def get_long_weibo(self, id):
        """获取长微博"""
        for i in range(3):
            url = 'https://m.weibo.cn/status/%s' % id
            html = requests.get(url).text
            html = html[html.find('"status":'):]
            html = html[:html.rfind('"hotScheme"')]
            html = html[:html.rfind(',')]
            html = '{' + html + '}'
            html = re.findall("""(.*?)]\[0] || \{};.*}""", html, re.S)[0]  # 修改re代码
            try:
                js = json.loads(html, strict=False)
                weibo_info = js.get('status')
                if weibo_info:
                    weibo = self.parse_weibo(weibo_info)
                    return weibo
            except:
                pass
            sleep(random.randint(3, 5))

    def parse_weibo(self, weibo_info):
        weibo = OrderedDict()
        if weibo_info['user']:
            weibo['user_id'] = weibo_info['user']['id']
            weibo['screen_name'] = weibo_info['user']['screen_name']
        else:
            weibo['user_id'] = ''
            weibo['screen_name'] = ''
        weibo['id'] = int(weibo_info['id'])
        weibo['weibo_url'] = f"https://m.weibo.cn/detail/{weibo_info['id']}"
        print(weibo['weibo_url']) # 添加微博链接字段
        weibo['bid'] = weibo_info['bid']
        text_body = weibo_info['text']
        selector = etree.HTML(text_body)
        weibo['text'] = etree.HTML(text_body).xpath('string(.)')
        weibo['text'] = self.clear_character_chinese(weibo['text'])
        weibo['pics'] = self.get_pics(weibo_info)
        weibo['video_url'] = self.get_video_url(weibo_info)
        weibo['location'] = self.get_location(selector)
        weibo['created_at'] = weibo_info['created_at']
        weibo['source'] = weibo_info['source']
        weibo['attitudes_count'] = self.string_to_int(
            weibo_info.get('attitudes_count', 0))
        weibo['comments_count'] = self.string_to_int(
            weibo_info.get('comments_count', 0))
        weibo['reposts_count'] = self.string_to_int(
            weibo_info.get('reposts_count', 0))
        weibo['topics'] = self.get_topics(selector, weibo['text'])
        weibo['at_users'] = self.get_at_users(selector)
        return self.standardize_info(weibo)

    # 去除字母数字表情和其它字符
    def clear_character_chinese(self, sentence):
        pattern1 = '[a-zA-Z0-9]'
        pattern2 = '\[.*?\]'
        pattern3 = re.compile(u'[^\s1234567890:：' + '\u4e00-\u9fa5]+')
        pattern4 = '[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+'
        line2 = re.sub(pattern2, '', sentence)  # 去除表情
        new_sentence = ''.join(line2.split())  # 去除空白
        return new_sentence

    def get_pics(self, weibo_info):
        """获取微博原始图片url"""
        if weibo_info.get('pics'):
            pic_info = weibo_info['pics']
            pic_list = [pic['large']['url'] for pic in pic_info]
            pics = ','.join(pic_list)
        else:
            pics = ''
        return pics

    def get_live_photo(self, weibo_info):
        """获取live photo中的视频url"""
        live_photo_list = []
        live_photo = weibo_info.get('pic_video')
        if live_photo:
            prefix = 'https://video.weibo.com/media/play?livephoto=//us.sinaimg.cn/'
            for i in live_photo.split(','):
                if len(i.split(':')) == 2:
                    url = prefix + i.split(':')[1] + '.mov'
                    live_photo_list.append(url)
            return live_photo_list

    def get_video_url(self, weibo_info):
        """获取微博视频url"""
        video_url = ''
        video_url_list = []
        if weibo_info.get('page_info'):
            if weibo_info['page_info'].get('media_info') and weibo_info[
                'page_info'].get('type') == 'video':
                media_info = weibo_info['page_info']['media_info']
                video_url = media_info.get('mp4_720p_mp4')
                if not video_url:
                    video_url = media_info.get('mp4_hd_url')
                    if not video_url:
                        video_url = media_info.get('mp4_sd_url')
                        if not video_url:
                            video_url = media_info.get('stream_url_hd')
                            if not video_url:
                                video_url = media_info.get('stream_url')
        if video_url:
            video_url_list.append(video_url)
        live_photo_list = self.get_live_photo(weibo_info)
        if live_photo_list:
            video_url_list += live_photo_list
        return ';'.join(video_url_list)

    def get_location(self, selector):
        """获取微博发布位置"""
        location_icon = 'timeline_card_small_location_default.png'
        span_list = selector.xpath('//span')
        location = ''
        for i, span in enumerate(span_list):
            if span.xpath('img/@src'):
                if location_icon in span.xpath('img/@src')[0]:
                    location = span_list[i + 1].xpath('string(.)')
                    break
        return location

    def get_topics(self, selector, context):
        """获取参与的微博话题"""
        span_list = selector.xpath("//span[@class='surl-text']")
        topics = ''
        topic_list = []
        for span in span_list:
            text = span.xpath('string(.)')
            if len(text) > 2 and text[0] == '#' and text[-1] == '#':
                topic_list.append(text[1:-1])
        if topic_list:
            topics = ';'.join(topic_list)
        if topics == '':
            context_list = re.findall('#(.*?)#', context, re.S)
            if context_list:
                topics = ';'.join(context_list)
        return topics

    def get_at_users(self, selector):
        """获取@用户"""
        a_list = selector.xpath('//a')
        at_users = ''
        at_list = []
        for a in a_list:
            if '@' + a.xpath('@href')[0][3:] == a.xpath('string(.)'):
                at_list.append(a.xpath('string(.)')[1:])
        if at_list:
            at_users = ','.join(at_list)
        return at_users

    def string_to_int(self, string):
        """字符串转换为整数"""
        if isinstance(string, int):
            return string
        elif string.endswith(u'万+'):
            string = int(string[:-2] + '0000')
        elif string.endswith(u'万'):
            string = int(string[:-1] + '0000')
        return int(string)

    def standardize_date(self, created_at):
        """标准化微博发布时间"""
        if u"刚刚" in created_at:
            created_at = datetime.now().strftime("%Y-%m-%d")
        elif u"分钟" in created_at:
            minute = created_at[:created_at.find(u"分钟")]
            minute = timedelta(minutes=int(minute))
            created_at = (datetime.now() - minute).strftime("%Y-%m-%d")
        elif u"小时" in created_at:
            hour = created_at[:created_at.find(u"小时")]
            hour = timedelta(hours=int(hour))
            created_at = (datetime.now() - hour).strftime("%Y-%m-%d")
        elif u"昨天" in created_at:
            day = timedelta(days=1)
            created_at = (datetime.now() - day).strftime("%Y-%m-%d")
        elif created_at.count('-') == 1:
            year = datetime.now().strftime("%Y")
            created_at = year + "-" + created_at
        return created_at

    def getTimeConvert(self,data):
        time_format=datetime.strptime(data,'%a %b %d %H:%M:%S %z %Y')
        time_format=str(time_format)
        times=time_format[0:10]
        return datetime.strptime(times, "%Y-%m-%d")

    # 获取全部微博的评论
    def get_comments(self):
        write_count = 0
        for mid in self.weibo_id_list:  # 遍历需要爬取评论的微博ID列表
            try:
                print(f"开始爬取微博 {mid} 的评论...")
                m_id = 0
                id_type = 0
                jsondata = self.get_comments_page(m_id, id_type, mid=mid)

                # 如果返回数据为空，直接标记为已完成
                if not jsondata or not jsondata.get('data'):
                    print(f"微博 {mid} 没有评论数据，直接标记为已完成。")
                    self.database.mark_comments_fetched(mid)
                    continue

                results = self.parse_comments_page(jsondata)

                # 确认是否有分页
                if results['max']:
                    maxpage = results['max']
                    print(f"微博 {mid} 的评论页数: {maxpage}")

                    for page in range(maxpage):
                        print(f"采集微博 {mid} 的第 {page+1} 页评论...")
                        jsondata = self.get_comments_page(m_id, id_type, mid)
                        datas = jsondata.get('data').get('data') if jsondata.get('data') else None

                        # 如果评论数据为空，跳过
                        if not datas:
                            print(f"微博 {mid} 的第 {page+1} 页没有评论，跳过。")
                            continue

                        # 将评论数据添加到缓存
                        self.add_comments_json(datas,mid)

                        # 每 10 条评论写入数据库
                        if len(self.comments) % 10 == 0:
                            self.comments_to_mysql(write_count)
                            write_count += 10

                        # 解析下一页的参数
                        results = self.parse_comments_page(jsondata)
                        m_id = results['max_id']
                        id_type = results['max_id_type']

                        # 随机休眠避免触发反爬
                        sleep(random.randint(2, 4))
                        if page % 30 == 0:  # 每 30 页长时间休眠
                            sleep(6)

                # 爬取完该微博的所有评论后，标记状态为已完成
                self.database.mark_comments_fetched(mid)
                print(f"微博 {mid} 的评论爬取完成，并已标记为已完成状态。")

            except Exception as e:
                # 出现任何异常时也标记为已完成
                print(f"爬取微博 {mid} 的评论时出错: {e}")
                print(f"将微博 {mid} 标记为已完成（可能没有评论或其他原因）。")
                self.database.mark_comments_fetched(mid)
                continue

        # 将剩余的评论写入数据库
        self.comments_to_mysql(write_count)
        print("所有微博的评论爬取已完成。")



    def add_comments_json(self,jsondata,mid):
        for data in jsondata:
            item = dict()
            item['id'] = data.get('id')
            item['mid'] = mid
            item['like_count'] = data.get("like_count")
            item['source'] = data.get("source")
            item['floor_number'] = data.get("floor_number")
            item['screen_name'] = data.get("user").get("screen_name")
            # 性别
            item['gender'] = data.get("user").get("gender")
            if(item['gender'] == 'm'):
                item['gender'] = '男'
            elif(item['gender'] == 'f'):
                item['gender'] = '女'
            item['rootid'] = data.get("rootid")
            item['create_time'] = data.get("created_at")
       
            import time
            item['create_time'] = time.strptime(item['create_time'], '%a %b %d %H:%M:%S %z %Y')
            item['create_time'] = time.strftime('%Y-%m-%d',item['create_time'])
            item['comment'] = data.get("text")
            item['comment'] = BeautifulSoup(item['comment'], 'html.parser').get_text()
            item['comment'] = self.clear_character_chinese(item['comment'])
            # 添加微博链接
        
            item['weibo_url'] = f"https://m.weibo.cn/detail/{mid}"  # 根据微博 ID 生成 URL
            # 打印微博链接
            print(f"微博链接: {item['weibo_url']}")
            print('当前楼层{},评论{}'.format(item['floor_number'],item['comment']))
            # 评论这条评论的信息
            comments = data.get("comments")
            if(comments):
                self.add_comments_json(comments,mid)
            # print jsondata.dumps(comment, encoding="UTF-8", ensure_ascii=False)
            self.comments.append(item)
            
    def get_comments_page(self,max_id, id_type,mid):
        from get_weibo_cookie import get_cookie
        params = {
            'max_id': max_id,
            'max_id_type': id_type
            }
        try:
            url = 'https://m.weibo.cn/comments/hotflow?id={id}&mid={mid}'
            headers = {
            'Cookie': '_T_WM=23954867679; WEIBOCN_FROM=1110006030; MLOGIN=1; SCF=AlcRVUdvBhSVRtoVQOsWjKCmiJgxqQZelzyZUFxL2jquCXtfiBwl0hOqi_WvaSy1E2OPb34HCwhEPukQ2XEw2jI.; SUB=_2A25KekP-DeRhGeNK71UQ-S_EzjWIHXVp9tk2rDV6PUJbktAYLWTckW1NSSiku5eakbGqIYNyENX5FBZ9r-rKNwg3; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5CZBNcBJmaKjCESo.Qnhjj5NHD95QfShBNeK.p1h-4Ws4DqcjKIFH8Sb-4xF-RxCH8SCHFxbHFSBtt; SSOLoginState=1736324015; ALF=1738916015; XSRF-TOKEN=2dbd94; mweibo_short_token=b8d2767479; M_WEIBOCN_PARAMS=oid%3D5075737352865499%26luicode%3D20000061%26lfid%3D5075740560982268%26uicode%3D20000061%26fid%3D5075737352865499',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
            'X-Requested-With': 'XMLHttpRequest'
        }
            r = requests.get(url.format(id=mid,mid=mid), params=params,headers=headers)
            time.sleep(random.randint(1,2))
            print(r.url)
            if r.status_code == 200:
                return r.json()
        except requests.ConnectionError as e:
            print('error', e.args)    
    
    def add_comments(self,jsondata):
        datas = jsondata.get('data').get('data')
        for data in datas:
            item = dict()
            item['id'] = data.get('id')
            item['mid'] = data.get('mid')
            item['like_count'] = data.get("like_count")
            item['source'] = data.get("source")
            item['floor_number'] = data.get("floor_number")
            item['screen_name'] = data.get("user").get("screen_name")
            # 性别
            item['gender'] = data.get("user").get("gender")
            if(item['gender'] == 'm'):
                item['gender'] = '男'
            elif(item['gender'] == 'f'):
                item['gender'] = '女'
            item['created_at'] = self.standardize_date(
                data.get(['created_at']))
            import time
            item['create_time'] = time.strptime(item['create_time'], '%a %b %d %H:%M:%S %z %Y')
            item['create_time'] = time.strftime('%Y-%m-%d',item['create_time'])
            item['rootid'] = data.get("rootid")
            
            item['comment'] = data.get("text")
            item['comment'] = BeautifulSoup(item['comment'], 'html.parser').get_text()
            item['comment'] = self.clear_character_chinese(item['comment'])
            print('当前楼层{},评论{}'.format(item['floor_number'],item['comment']))
            # 评论这条评论的信息
            comments = data.get("comments")

            # print jsondata.dumps(comment, encoding="UTF-8", ensure_ascii=False)
            self.comments.append(item)

    def parse_comments_page(self,jsondata):
        if jsondata:
            items = jsondata.get('data')
            item_max_id = {}
            item_max_id['max_id'] = items['max_id']
            item_max_id['max_id_type'] = items['max_id_type']
            item_max_id['max'] = items['max']
            return item_max_id    

    def weibo_to_mysql(self, wrote_count):
        """将爬取的微博信息写入MySQL数据库"""
        mysql_config = {
        }
        weibo_list = []
        retweet_list = []
        info_list = self.weibo[wrote_count:]
        for w in info_list:
            w['text'] = self.filter_emoji(w['text'], restr='')  ###删除特殊符号
            if 'retweet' in w:
                w['retweet']['retweet_id'] = ''
                retweet_list.append(w['retweet'])
                w['retweet_id'] = w['retweet']['id']
                del w['retweet']
            else:
                w['retweet_id'] = ''
            weibo_list.append(w)
        # 在'weibo'表中插入或更新微博数据
        self.mysql_insert(mysql_config, 'weibo', retweet_list)
        self.mysql_insert(mysql_config, 'weibo', weibo_list)
        print(u'%d条微博写入MySQL数据库完毕' % self.got_count)

    def comments_to_mysql(self,write_count):
        """将爬取的用户信息写入MySQL数据库"""
        mysql_config = {
        }
        self.mysql_insert(mysql_config, 'comments', self.comments[write_count:])

    def mysql_insert(self, mysql_config, table, data_list):
        """向MySQL表插入或更新数据"""
        import pymysql

        if len(data_list) > 0:
            keys = ', '.join(data_list[0].keys())
            values = ', '.join(['%s'] * len(data_list[0]))
            if self.mysql_config:
                mysql_config = self.mysql_config
            connection = pymysql.connect(**mysql_config)
            cursor = connection.cursor()
            sql = """INSERT INTO {table}({keys}) VALUES ({values}) ON
                     DUPLICATE KEY UPDATE""".format(table=table,
                                                    keys=keys,
                                                    values=values)
            update = ','.join([
                " {key} = values({key})".format(key=key)
                for key in data_list[0]
            ])
            sql += update
            try:
                cursor.executemany(
                    sql, [tuple(data.values()) for data in data_list])
                connection.commit()
            except Exception as e:
                connection.rollback()
                print('Error: ', e)
                traceback.print_exc()
            finally:
                connection.close()

    

    
if __name__ == "__main__":
    data_spider = data_spider()
    data_spider.start_spider()
    # aa = data_spider.getTimeConvert('Fri Jan 01 09:18:07 +0800 2021')
    # print(datetime.strftime(aa, "%Y-%m-%d"))
    # test()




    
