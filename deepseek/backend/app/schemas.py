from pydantic import BaseModel
from datetime import datetime
from typing import List
class MessageBase(BaseModel):
    role: str
    content: str

class ChatCreate(BaseModel):
    message: str  # 用户发来的第一句话

class ChatResponse(BaseModel):
    reply: str
    remaining_balance: float

# 1. 用户注册时发给后端的数据
class UserCreate(BaseModel):
    username: str
    password: str

# 2. 用户注册成功后，后端回给前端的数据
#不能包含 password！
class UserResponse(BaseModel):
    id: int
    username: str
    balance: float
    # 它告诉 Pydantic: "如果不给你 JSON，给你一个数据库对象(ORM Object)，你自己看着办把它转成 JSON"
    class Config:
        from_attributes = True

# 新建会话只需要标题
class ChatSessionCreate(BaseModel):
    title: str = "New Chat"

# 返回会话详情
class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    class Config:
        from_attributes = True

# 返回历史消息
class ChatMessageResponse(BaseModel):
    role: str
    content: str
    timestamp: datetime
    class Config:
        from_attributes = True