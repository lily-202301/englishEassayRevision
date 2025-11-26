import requests
import threading
import time
import os
import json

# ==================================================
# --- 配置 ---
# ==================================================
API_URL_SUBMIT = "http://127.0.0.1:8000/grade_essay"
API_URL_RESULT = "http://127.0.0.1:8000/result/{task_id}"
IMAGE_PATH = "优秀5-1.jpg" 
CONCURRENT_REQUESTS = 10
POLLING_INTERVAL = 2  # 轮询间隔（秒）

# ==================================================
# --- 全局变量 ---
# ==================================================
# 存储每个任务的信息
# { "task_id": string, "start_time": float, "status": string, "end_time": float, "result": dict }
task_registry = []
lock = threading.Lock()

# ==================================================
# --- 函数定义 ---
# ==================================================

def submit_single_task(request_num):
    """提交单个任务并注册"""
    try:
        with open(IMAGE_PATH, 'rb') as f:
            image_filename = os.path.basename(IMAGE_PATH)
            files = {'images': (image_filename, f, 'image/jpeg')}
            
            start_time = time.time()
            response = requests.post(API_URL_SUBMIT, files=files)
            
            if response.status_code == 202:
                task_id = response.json().get('task_id')
                with lock:
                    task_registry.append({
                        "task_id": task_id,
                        "start_time": start_time,
                        "status": "SUBMITTED",
                        "end_time": None,
                        "result": None
                    })
                print(f"[提交线程] 任务 {request_num} 提交成功, Task ID: {task_id}")
            else:
                print(f"[提交线程] 任务 {request_num} 提交失败, 状态码: {response.status_code}")
    except Exception as e:
        print(f"[提交线程] 任务 {request_num} 发生异常: {e}")

def poll_results():
    """轮询所有未完成任务的结果"""
    while True:
        with lock:
            # 找到所有还未完成的任务
            pending_tasks = [task for task in task_registry if task['status'] not in ('SUCCESS', 'FAILURE')]
        
        if not pending_tasks:
            print("\n[轮询线程] 所有任务已完成，轮询结束。")
            break

        completed_count = len(task_registry) - len(pending_tasks)
        print(f"\n[轮询线程] 进度: {completed_count}/{len(task_registry)} | 正在检查 {len(pending_tasks)} 个剩余任务...")
        for task_info in pending_tasks:
            try:
                url = API_URL_RESULT.format(task_id=task_info['task_id'])
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status')
                    if status in ('SUCCESS', 'FAILURE'):
                        with lock:
                            task_info['status'] = status
                            task_info['end_time'] = time.time()
                            task_info['result'] = data.get('result')
                        print(f"[轮询线程] 任务 {task_info['task_id'][:8]}... 状态更新: {status}")
            except requests.RequestException as e:
                print(f"[轮询线程] 查询任务 {task_info['task_id'][:8]}... 出错: {e}")
        
        time.sleep(POLLING_INTERVAL)

def analyze_results():
    """分析并打印最终的性能报告"""
    print("\n" + "="*30 + " 压力测试性能报告 " + "="*30)
    
    successful_tasks = [t for t in task_registry if t['status'] == 'SUCCESS' and t['end_time'] is not None]
    failed_tasks = [t for t in task_registry if t['status'] != 'SUCCESS']

    print(f"总任务数: {len(task_registry)}")
    print(f"成功任务: {len(successful_tasks)}")
    print(f"失败任务: {len(failed_tasks)}")

    if not successful_tasks:
        print("\n没有成功完成的任务，无法进行性能分析。")
        return

    # --- 性能指标计算 ---
    total_times = [t['end_time'] - t['start_time'] for t in successful_tasks]
    json_times = [t['result']['timing']['json_generation'] for t in successful_tasks if t['result'] and 'timing' in t['result']]
    pdf_times = [t['result']['timing']['pdf_generation'] for t in successful_tasks if t['result'] and 'timing' in t['result']]

    print("\n--- 整体性能 (从提交到PDF生成) ---")
    print(f"平均耗时: {sum(total_times) / len(total_times):.2f} 秒")
    print(f"最快耗时: {min(total_times):.2f} 秒")
    print(f"最慢耗时: {max(total_times):.2f} 秒")

    if json_times:
        print("\n--- 阶段耗时 --- (基于成功任务的结果)")
        print(f"平均JSON生成耗时: {sum(json_times) / len(json_times):.2f} 秒")
        print(f"平均PDF生成耗时: {sum(pdf_times) / len(pdf_times):.2f} 秒")
    
    print("="*80 + "\n")

# ==================================================
# --- 主程序 ---
# ==================================================
if __name__ == "__main__":
    print(f"--- 开始压力测试: {CONCURRENT_REQUESTS} 个并发请求 ---")
    if IMAGE_PATH == "path/to/your/test_image.jpg" or not os.path.exists(IMAGE_PATH):
        print(f"\n⛔️ 错误: 请先修改 stress_test.py 文件中的 IMAGE_PATH 再运行。")
        exit()

    # --- 1. 并发提交任务 ---
    submission_threads = []
    for i in range(CONCURRENT_REQUESTS):
        thread = threading.Thread(target=submit_single_task, args=(i + 1,))
        submission_threads.append(thread)
        thread.start()
        time.sleep(0.01)
    
    for thread in submission_threads:
        thread.join()
    
    print(f"\n--- 所有 {len(task_registry)} 个任务已提交完毕 ---")
    total_start_time = time.time()

    # --- 2. 启动轮询线程 ---
    polling_thread = threading.Thread(target=poll_results)
    polling_thread.start()
    polling_thread.join() # 等待轮询结束

    total_end_time = time.time()
    print(f"\n--- 所有任务处理完成，总计用时: {total_end_time - total_start_time:.2f} 秒 ---")

    # --- 3. 分析并打印报告 ---
    analyze_results()
