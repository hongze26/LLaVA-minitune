host_ip = "localhost"  # 你的mysql服务器地址
host_user = "root"
password = "Hongze266."  # 你的mysql密码
db = 'yuqing'
port = 3306
charset= 'utf8mb4'

# 配置需要采集的内容 'weibo'
spider_list = ['weibo']

weibo_config = {
    "user_id": "1891849065",  # 修改
    "filter": 1,
    "cookie": "_T_WM=74307132980; WEIBOCN_FROM=1110006030; XSRF-TOKEN=fe208f; mweibo_short_token=cd8e7bb82f; SCF=AlcRVUdvBhSVRtoVQOsWjKCmiJgxqQZelzyZUFxL2jquFH3neygPI6lduVTHnCFwob56Oao6Murtx0DSeMSebW0.; SUB=_2A25KeJBXDeRhGeNK71UQ-S_EzjWIHXVp962frDV6PUJbktAYLUXykW1NSSiku1UdAJfyYBhoMuBJYSATt5sc3k1M; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5CZBNcBJmaKjCESo.Qnhjj5JpX5KMhUgL.Fo-XShMp1K2RSK.2dJLoIpSQi--ciKL2iKy8i--fi-isi-zf; SSOLoginState=1736237063; ALF=1738829063; MLOGIN=1; M_WEIBOCN_PARAMS=luicode%3D20000174%26uicode%3D20000174",
    "mysql_config": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "Hongze266.",
        "charset": "utf8mb4",
        "db":"yuqing"
    }
}