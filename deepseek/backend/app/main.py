from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from .app import models, schemas, database, service, auth,worker
import logging
from typing import List
# 1. 创建数据库表
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# 获取数据库会话的工具函数
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 新增依赖函数: 根据 Token 找用户 ---
def get_current_user(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# --- 1. 注册接口 ---
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- 2. 登录接口 (获取 Token) ---
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- 3. 聊天接口  ---
# 1. 创建新会话
@app.post("/sessions", response_model=schemas.ChatSessionResponse)
def create_session(session_data: schemas.ChatSessionCreate, 
                   current_user: models.User = Depends(get_current_user), 
                   db: Session = Depends(get_db)):
    new_session = models.ChatSession(user_id=current_user.id, title=session_data.title)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

# 2. 获取我的所有会话
@app.get("/sessions", response_model=List[schemas.ChatSessionResponse])
def get_user_sessions(current_user: models.User = Depends(get_current_user), 
                      db: Session = Depends(get_db)):
    return current_user.chats

# 注意：现在的参数 user 是通过 get_current_user 自动查出来的真用户
@app.post("/sessions/{session_id}/chat")
def chat_in_session(session_id: int, chat_input: schemas.ChatCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. 检查会话 (和以前一样)
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id, models.ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 2. 准备上下文 (和以前一样)
    history_records = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).order_by(models.ChatMessage.timestamp).all()
    context_messages = [{"role": msg.role, "content": msg.content} for msg in history_records]
    context_messages.append({"role": "user", "content": chat_input.message})

    # 3. 【关键变化】不再直接调用 service，而是调用 worker.delay()
    # .delay() 方法会把任务打包发给 Redis，然后立刻返回一个 Task 对象，不会卡住！
    task = worker.chat_task.delay(context_messages)

    # 4. 我们先存用户说的话 (因为 AI 还没回，所以没法存 AI 的话)
    user_msg = models.ChatMessage(session_id=session_id, role="user", content=chat_input.message)
    db.add(user_msg)
    current_user.balance -= 0.1
    db.commit()

    # 5. 返回任务 ID 给前端
    # 前端拿到这个 ID 后，需要每隔 1 秒来问一次：“任务好了吗？”
    return {
        "reply": "Processing...", 
        "task_id": task.id, 
        "status": "queued",
        "remaining_balance": current_user.balance
    }
    










