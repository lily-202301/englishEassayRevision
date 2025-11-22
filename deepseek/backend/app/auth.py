from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, database
from dotenv import load_dotenv
import os
# 1. 配置：密钥 (生产环境要藏在环境变量里！)
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# 2. 密码加密工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 3. 前端发 Token 给后端的“暗号”位置 (Header: Authorization: Bearer <token>)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    参数:
    - data: 我们要写在手环里的信息（比如用户名 {"sub": "zhangsan"}）。
    - expires_delta: 可选参数。这张票多久过期？如果不填就用默认值。
    """
    
    # 1. 复制一份数据
    # 为什么要 copy？因为 Python 的字典是引用传递。
    # 如果我们直接改 data，可能会影响到函数外面传进来的那个原始变量。为了安全，先复印一份。
    to_encode = data.copy()
    
    # 2. 计算“作废时间” (Expiration Time)
    if expires_delta:
        # 如果调用这个函数时指定了时间（比如“这张票只能用5分钟”），就按指定的算。
        # datetime.utcnow() 获取当前的 UTC 国际标准时间。
        expire = datetime.utcnow() + expires_delta
    else:
        # 如果没指定，就用我们全局配置的默认值（比如 30 分钟）。
        # timedelta(minutes=...) 是用来做时间加减法的工具。
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 3. 把作废时间写进字典
    # "exp" 是 JWT 国际标准里规定的字段名，全称 Expiration Time。
    # 这一点很重要！因为后续验证 Token 的库（python-jose）会自动找 "exp" 这个字段。
    # 如果发现当前时间 > exp，它会直接报错说 "Token expired"，连代码都不用你自己写。
    to_encode.update({"exp": expire})
    
    # 4. 核心加密步骤 —— 签字盖章 (Sign)
    # 这一步是魔法发生的地方。
    # jwt.encode 接收三个参数：
    #   1. to_encode: 内容（比如：{"sub": "zhangsan", "exp": 1715690000}）
    #   2. SECRET_KEY: 你的私章（玉玺）。只有你有，别人没有。
    #   3. algorithm: 盖章的手法（HS256）。
    #
    # 结果：它会生成一长串字符串，比如 "eyJhbGciOi..."
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # 5. 返回这一长串字符串
    return encoded_jwt