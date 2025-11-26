import os
import base64
import json
import uuid
import time
import subprocess
import dirtyjson
from datetime import datetime
from openai import OpenAI
from celery_utils import celery_app
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 1. 配置
# ==========================================
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError("错误：找不到 API Key。...")

client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    timeout=120.0,
    max_retries=3,
)

RUNS_FOLDER = 'runs'
if not os.path.exists(RUNS_FOLDER):
    os.makedirs(RUNS_FOLDER)

# ==========================================
# 2. 标准化、无歧义的 System Prompt
# ==========================================
SYSTEM_PROMPT = """# Role Definition
你是一位经验丰富的英语作文阅卷专家。学生书写也是评分的依据，你的任务是针对我提供的[学生英语作文](图片形式)，按照指定的维度进行深度批改，并输出一个严格符合格式要求的 JSON 数据。

# Input Data
- 学生身份：高中生
- 作文内容：图片中的手写文字(若有多张图片，请合并阅读)

# Task Requirements
请仔细阅读作文，进行多维度的分析，你需要完成以下 JSON 字段的填充：

1. **original_text**: [OCR识别]准确识别图片中的手写英文，将所有图片内容合并为一段完整的文本。
2. **overall_evaluation**: 给出档次、总分、简短评语及四个维度的细分打分。
3. **highlights**: 分析内容、语言、结构三个方面的亮点。
4. **improvements**: 分析内容、语言、结构三个方面的待提升点。
5. **error_summary**: 总结出现的错误类型。
6. **detailed_errors**: 逐句列出具体错误、修正及解释。
7. **optimizations**: 选取表达平淡的句子进行升格润色。
8. **paragraph_reviews**: 分段点评。
9. **material_reuse_guide**: 一材多用分析。
10. **revised_text**: [范文输出]基于原文，在吸纳上述所有修改建议后，输出一篇完整的、高质量的修正版作文。

# Output Format (JSON Schema)
请严格按照以下 JSON 结构输出，不要包含 markdown 代码块标记，直接输出纯文本 JSON 字符串。

{
  "original_text": "STRING: 识别到的作文原文(合并所有图片内容)",
  "overall_evaluation": {
    "tier": "STRING: 评定档次 (最好: 第五档, 最差: 第一档)",
    "total_score": "STRING: 总分(满分25分，5分为一个分界)",
    "brief_comment": "STRING: 1-2句总体简评",
    "score_breakdown": {
      "relevance": "STRING: 切题程度",
      "grammar_vocab": "STRING: 语法词汇",
      "logic_structure": "STRING: 逻辑结构",
      "content": "STRING: 内容充实度"
    }
  },
  "highlights": {
    "content": [ { "point": "STRING", "evidence": "STRING" } ],
    "language": [ { "point": "STRING", "evidence": "STRING" } ],
    "structure": [ { "point": "STRING", "description": "STRING" } ]
  },
  "improvements": {
    "content": [ { "point": "STRING", "description": "STRING" } ],
    "language": [ { "point": "STRING", "evidence": "STRING" } ],
    "structure": [ { "point": "STRING", "description": "STRING" } ]
  },
  "error_summary": {
    "grammar": ["STRING"],
    "spelling": ["STRING"],
    "structure": ["STRING"]
  },
  "detailed_errors": [
    {
      "id": "NUMBER",
      "type": "STRING",
      "original_sentence": "STRING",
      "correction": "STRING",
      "explanation": "STRING",
      "advanced_suggestion": "STRING"
    }
  ],
  "optimizations": [
    {
      "id": "NUMBER",
      "type": "STRING",
      "original_sentence": "STRING",
      "correction": "STRING",
      "explanation": "STRING"
    }
  ],
  "paragraph_reviews": [
    {
      "paragraph_index": "NUMBER",
      "summary": "STRING",
      "issues": "STRING",
      "specific_corrections": [ { "wrong": "STRING", "right": "STRING" } ]
    }
  ],
  "material_reuse_guide": {
    "applicable_themes": [
      {
        "theme": "STRING",
        "description": "STRING"
      }
    ],
    "processing_direction": "STRING",
    "expansion_ideas": "STRING"
  },
  "revised_text": "STRING: [此处输出最终的修正版范文]"
}
"""

# ==========================================
# 3. Celery 任务 (最终修复版)
# ==========================================

@celery_app.task
def grade_essay_multipage(image_path_list, prompt_text):
    start_time = time.time()
    user_content_list = []
    for img_path in image_path_list:
        base64_str = encode_image(img_path)
        if base64_str:
            user_content_list.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_str}"}})
    if not user_content_list:
        return {"error": "No valid images loaded."}
    user_content_list.append({"type": "text", "text": prompt_text})
    try:
        completion = client.chat.completions.create(
            model="qwen-vl-max",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content_list},
            ],
            temperature=0.2,
        )
        raw_content = completion.choices[0].message.content
        clean_content = raw_content.replace("```json", "").replace("```", "").strip()
        if not clean_content:
            raise ValueError("API返回了空内容")
        json_generation_time = time.time() - start_time
        print(f"✅ [JSON Task] 批改完成, 耗时: {json_generation_time:.2f}s")
        return {"json_result": clean_content, "timing": {"json_generation": json_generation_time}}
    except Exception as e:
        print(f"💥 [JSON Task] API 调用出错: {e}")
        return {"error": str(e)}

@celery_app.task
def generate_pdf_report(previous_result):
    if 'error' in previous_result:
        return previous_result

    start_time = time.time()
    json_string = previous_result['json_result']

    run_dir = os.path.join(RUNS_FOLDER, datetime.now().strftime('%Y%m%d-%H%M%S') + f"_{uuid.uuid4().hex[:6]}")
    os.makedirs(run_dir, exist_ok=True)

    json_path = os.path.join(run_dir, "qwen_essay_result.json")
    pdf_path = os.path.join(run_dir, "essay_report.pdf")

    try:
        # 1. 使用 dirtyjson 容错解析并保存JSON
        try:
            data = dirtyjson.loads(json_string)
        except Exception as e:
            with open(json_path + ".error.txt", "w", encoding="utf-8") as f:
                f.write(json_string)
            raise ValueError(f"LLM返回了无效的JSON数据且无法自动修复: {e}")
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 2. 构建并执行命令行
        command = [
            "node", 
            "export-pdf.js", 
            f"--json={json_path}", 
            f"--out={pdf_path}"
        ]
        print(f"📄 [PDF Task] 正在执行命令: {' '.join(command)}")
        
        result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
        print(f"✅ [PDF Task] export-pdf.js 脚本执行成功。")

        pdf_generation_time = time.time() - start_time
        print(f"✅ [PDF Task] PDF 和 JSON 已保存至: {run_dir}")

        return {
            "json_path": json_path,
            "pdf_path": pdf_path,
            "timing": {
                "json_generation": previous_result['timing']['json_generation'],
                "pdf_generation": pdf_generation_time,
                "total": previous_result['timing']['json_generation'] + pdf_generation_time
            }
        }

    except subprocess.CalledProcessError as e:
        print(f"💥 [PDF Task] export-pdf.js 脚本执行失败:")
        print(f"--- STDOUT ---\n{e.stdout}")
        print(f"--- STDERR ---\n{e.stderr}")
        return {"error": f"PDF generation script failed: {e.stderr}"}
    except Exception as e:
        print(f"💥 [PDF Task] 生成 PDF 时出现意外错误: {e}")
        return {"error": f"PDF generation failed: {e}"} 


def encode_image(image_path):
    if not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
