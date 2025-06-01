import json

from snownlp import SnowNLP
from database_util import database_util
from multi_modal_utils import analysis
# 情感分析
class NLPUTIL:
    def __init__(self):
        self.database = database_util()

    def get_nlp_result(self,text,img_url):
        try:
            nlp = analysis(text,img_url)
            print(nlp)
            sq = json.loads(nlp.replace('json', '').replace('```', ''))
            print(sq)
            score = sq['sentiment']
            print(score)
            if(score=='negative'):
                return '消极'
            elif(score=='positive'):
                return '积极'
            else:
                return '中立'
        except Exception as e:
            print(e)
            return '中立'

    def build_nlp_result(self):
        """
        构建NLP处理结果。
        本函数从数据库查询NLP数据，对每个数据项进行处理，如果数据项未在NLP详细信息中记录，
        且内容非空，则对其进行NLP处理，并保存处理结果。
        """
        # 从数据库查询NLP数据
        data = self.database.query_nlp_data()

        # 遍历查询到的NLP数据项
        for item in data:
            # 检查数据库中是否已有该数据项的NLP详细信息
            flag = self.database.check_nlp_detail(item['source'], item['id'])

            # 如果已记录详细信息，则跳过当前数据项
            if (flag):
                continue

            # 如果数据项内容为空，则跳过当前数据项
            if (item['content'] == None or item['content'] == ''):
                continue

            # 对数据项内容进行NLP处理，并将结果存储在item字典中
            item['nlp'] = self.get_nlp_result(item['content'],
                                              "https://image.baidu.com/search/down?url=" + item['img_url'])

            # 保存NLP处理结果
            self.database.save_nlp_result(item)


if __name__ == "__main__":
    nlp = NLPUTIL()
    nlp.build_nlp_result()