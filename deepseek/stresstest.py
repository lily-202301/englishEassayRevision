import requests
import time
import threading
import sys

# --- 🟢 配置区域 (在这里改并发数) ---
SERVER_URL = "http://119.45.187.169:8000"  # 你的服务器IP
USERNAME = "yty"
PASSWORD = "123456"
CONCURRENT_USERS = 10  # 👈 想要测 50 或 100，改这里！
POLL_INTERVAL = 1.0    # 每隔几秒去问一次结果
# --------------------------------

def get_token():
    """登录获取 Token"""
    try:
        # 1. 尝试注册 (避免用户不存在)
        requests.post(f"{SERVER_URL}/register", json={"username": USERNAME, "password": PASSWORD})
    except:
        pass

    # 2. 登录
    resp = requests.post(f"{SERVER_URL}/token", data={"username": USERNAME, "password": PASSWORD})
    if resp.status_code != 200:
        print(f"❌ 登录失败: {resp.text}")
        sys.exit(1)
    return resp.json()["access_token"]

def create_session(token):
    """创建会话"""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{SERVER_URL}/sessions", json={"title": "Stress Test"}, headers=headers)
    return resp.json()["id"]

def poll_result(task_id):
    """轮询直到获取结果"""
    while True:
        try:
            resp = requests.get(f"{SERVER_URL}/tasks/{task_id}")
            data = resp.json()
            if data["status"] == "Completed":
                return data["result"]
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            return f"Error polling: {e}"

def worker_thread(user_id, session_id, token):
    """模拟单个用户的完整行为"""
    headers = {"Authorization": f"Bearer {token}"}
    msg = f"你好 DeepSeek，这是第 {user_id} 号并发测试，请简短回复。"
    
    start_time = time.time()
    
    # 1. 发送请求 (瞬间完成)
    try:
        resp = requests.post(
            f"{SERVER_URL}/sessions/{session_id}/chat", 
            json={"message": msg}, 
            headers=headers
        )
        if resp.status_code != 200:
            print(f"🔴 [用户 {user_id}] 请求失败: {resp.text}")
            return
            
        task_data = resp.json()
        task_id = task_data.get("task_id")
        
        queue_time = time.time() - start_time
        print(f"🎫 [用户 {user_id}] 已领号 (耗时 {queue_time:.2f}s) -> 等待出餐...")
        
        # 2. 轮询结果 (等待耗时)
        final_reply = poll_result(task_id)
        
        total_time = time.time() - start_time
        
        # 打印简略结果 (防止刷屏)
        preview = final_reply[:20].replace('\n', ' ') + "..."
        print(f"✅ [用户 {user_id}] 拿到结果! 总耗时: {total_time:.2f}s | 回复: {preview}")

    except Exception as e:
        print(f"❌ [用户 {user_id}] 异常: {e}")

def main():
    print(f"🚀 准备开始压测 | 目标服务器: {SERVER_URL}")
    print(f"👥 并发用户数: {CONCURRENT_USERS}")
    
    token = get_token()
    session_id = create_session(token)
    print(f"🔑 登录成功，会话ID: {session_id}\n")
    
    threads = []
    global_start = time.time()

    # 启动所有线程
    for i in range(1, CONCURRENT_USERS + 1):
        t = threading.Thread(target=worker_thread, args=(i, session_id, token))
        threads.append(t)
        t.start()
        # 稍微错开一点点启动时间，更模拟真实情况
        time.sleep(0.05) 

    # 等待所有线程结束
    for t in threads:
        t.join()

    total_duration = time.time() - global_start
    print(f"\n🏁 压测结束! {CONCURRENT_USERS} 个请求全部处理完毕。")
    print(f"⏱️ 总计耗时: {total_duration:.2f}s")
    print(f"⚡ 平均吞吐量 (QPS): {CONCURRENT_USERS / total_duration:.2f} requests/s")

if __name__ == "__main__":
    main()