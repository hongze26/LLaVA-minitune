import pymysql
from sqlalchemy import text

from config import *
import datetime
from time_util import get_last_week

# 数据库工具
class database_util:
    def __init__(self):
        self.conn = pymysql.connect(host=host_ip, port=port, user=host_user, passwd=password, db=db, charset=charset)
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)


    # 从数据库中获取微博ID
    def query_weibo_ids(self):
        query_sql = 'SELECT id FROM weibo'
        self.cursor.execute(query_sql)
        data = self.cursor.fetchall()
        return data  # 返回一个包含微博ID的字典列表，例如：[{'id': 123}, {'id': 456}]
    
    # 获取评论未爬取完成的微博
    def get_unfinished_weibo(self):
        query_sql = 'SELECT id FROM weibo WHERE comments_fetched = 0 ORDER BY created_at ASC'
        self.cursor.execute(query_sql)
        data = self.cursor.fetchall()
        return [item['id'] for item in data]  # 返回未完成评论爬取的微博ID列表

    # 将指定微博的评论标记为已完成
    def mark_comments_fetched(self, weibo_id):
        update_sql = 'UPDATE weibo SET comments_fetched = 1 WHERE id = %s'
        self.cursor.execute(update_sql, [weibo_id])
        self.conn.commit()



    # 存储学校新闻
    def save_news(self,data_list):
        sql = 'insert school_news(title,create_time,creator,content,link) VALUES (%s,%s,%s,%s,%s)'
        for data in data_list:
            values = [data['title'], data['create_time'], data['creator'], data['content'], data['link']]
            self.cursor.execute(text(sql), values)
        self.conn.commit()

    # 查询学校新闻
    def query_news(self,title):
        query_sql = 'select count(1) as count from school_news where title = %s'
        values = [title]
        self.cursor.execute(query_sql,values)
        data = self.cursor.fetchone()
        if(data['count'] > 0):
            return True
        else:
            return False

     # 查询近一周的学校新闻
    def query_last_week_news(self):
        query_sql = 'select title  from school_news where create_time>= %s and create_time<=%s'
        start_time,end_time = get_last_week()
        values = [start_time,end_time]
        self.cursor.execute(query_sql,values)
        data = self.cursor.fetchall()
        data_list = list(data)
        result_list = []
        for item in data_list:
            result_list.append(item['title'])
        return ";".join(result_list)

     # 查询近一周的学校微博热词
    def query_last_week_weibo(self):
        query_sql = 'select text as title  from weibo where created_at>= %s and created_at<=%s'
        start_time,end_time = get_last_week()
        values = [start_time,end_time]
        self.cursor.execute(query_sql,values)
        data = self.cursor.fetchall()
        data_list = list(data)
        result_list = []
        for item in data_list:
            result_list.append(item['title'])
        return ";".join(result_list)

    # 查询近一周的学校微博热词
    def query_last_week_weibo_topic(self):
        query_sql = 'select topics as title  from weibo where created_at>= %s and created_at<=%s'
        start_time,end_time = get_last_week()
        values = [start_time,end_time]
        self.cursor.execute(query_sql,values)
        data = self.cursor.fetchall()
        data_list = list(data)
        result_list = []
        for item in data_list:
            result_list.append(item['title'])
        return ";".join(result_list)

    # 存储贴吧数据
    def save_tieba(self,data):
        sql = 'insert tieba(title,create_time,creator,content,link) VALUES (%s,%s,%s,%s,%s)'
        values = [data['title'],data['create_time'],data['creator'],data['content'],data['link']]
        self.cursor.execute(text(sql),values)
        self.conn.commit()

    def query_tieba(self,link):
        query_sql = 'select count(1) as count from tieba where link = %s'
        values = [link]
        self.cursor.execute(query_sql,values)
        data = self.cursor.fetchone()
        if(data['count'] > 0):
            return True
        else:
            return False

     # 存储贴吧数据
    def save_tieba_reply(self,data):
        sql = 'insert tieba_reply(reply_id,creator,create_time,content,link) VALUES (%s,%s,%s,%s,%s)'
        values = [data['reply_id'],data['creator'],data['create_time'],data['content'],data['link']]
        # print(values)
        self.cursor.execute(text(sql),values)
        self.conn.commit()

    def query_tieba_reply(self,reply_id):
        query_sql = 'select count(1) as count from tieba_reply where reply_id = %s'
        values = [reply_id]
        self.cursor.execute(query_sql,values)
        data = self.cursor.fetchone()
        if(data['count'] > 0):
            return True
        else:
            return False


    def query_nlp_data(self):
        query_sql = "SELECT SS.* FROM (select a.id,a.comment as content,a.screen_name as creator,a.create_time,a.weibo_url as link,'微博' as source,b.pics as img_url from comments a INNER JOIN  weibo b on a.mid=b.id) SS \
            ORDER BY SS.create_time desc"
        self.cursor.execute(query_sql)
        data = self.cursor.fetchall()
        data_list = list(data)
        result_list = []
        for item in data_list:
            result_list.append({'id':item['id'],'content':item['content'],'source':item['source']
            ,'creator':item['creator'],'link':item['link'],'create_time':item['create_time'],'img_url':item['img_url']})
        return result_list

    def check_nlp_detail(self,source,orgin_id):
        query_sql = 'select count(1) as count from nlp_result where source = %s and orgin_id=%s'
        values = [source,orgin_id]
        self.cursor.execute(query_sql,values)
        data = self.cursor.fetchone()
        if(data['count'] > 0):
            return True
        else:
            return False


    def save_nlp_result(self,data):
        print(data)
        sql = 'insert nlp_result(content,nlp,creator,create_time,orgin_id,source,url) VALUES (%s,%s,%s,%s,%s,%s,%s)'
        values = [data['content'],data['nlp'],data['creator'],data['create_time'],data['id'],data['source'],data['link']]
        self.cursor.execute(sql,values)
        self.conn.commit()