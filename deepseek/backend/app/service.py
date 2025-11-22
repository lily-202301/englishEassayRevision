from openai import OpenAI
import os
from dotenv import load_dotenv
import os

load_dotenv()  # 加载 .env 文件


# DeepSeek 的 API 地址和 Key (从环境变量读取，不要写死在代码里！)
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"), 
    base_url="https://api.deepseek.com" 
)

def chat_with_deepseek(messages):
    """
    messages 格式: [{"role": "user", "content": "你好"}]
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False # 暂时先做非流式，简单点
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return "AI 暂时掉线了，请稍后再试。"