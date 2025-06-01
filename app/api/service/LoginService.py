"""
登录服务类
"""
import datetime

from sqlalchemy import inspect

from app.api.model.errors import ResponseCode,ResponseResult
from app import db
from app.api.model.Models import User
from app.api.service.UserService import UserService
userService = UserService()

class LoginService:

    # 用户登录
    def login(self,phone,password):
        try:
            print(phone)
            print(password)
            #user = User.query.filter_by(phone=str(phone),password=str(password)).first()

            # 打印生成的SQL语句
            query = User.query.filter_by(phone=phone, password=password)
            print("生成的SQL:", str(query))

            user = query.first()
            print(f"查询结果: {user}")

            # 检查数据库表结构
            inspector = inspect(db.engine)
            columns = inspector.get_columns('user')
            print("数据库字段类型:", [(c['name'], c['type']) for c in columns])
            print(user)
            if(user):
                return ResponseResult.success(data=user.to_json())
            else:
                return ResponseResult.error(ResponseCode.LOGIN_ERROR)
        except:
            return ResponseResult.error()

    # 用户注册
    def register(self,user_name, phone, password, email):
        user = userService.get_user_by_phone(phone)
        if(user):
            return ResponseResult.error(ResponseCode.PHONE_EXIST_ERROR)
        return userService.add_user(user_name, phone, password, email)

    

    


