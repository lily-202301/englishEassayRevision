import os
import base64
import json
import argparse
from openai import OpenAI

# ==========================================
# 1. 配置 API Key
# ==========================================
client = OpenAI(
    # ⚠️ 请确认此处填入的是有效的 API Key
    api_key="sk-c1a452ab4ec14d42ba9dfc629ff0463d",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# ==========================================
# 2. 定义完整的 System Prompt (顺序已调整)
# ==========================================
SYSTEM_PROMPT = """
# Role Definition
你是一位经验丰富的英语作文阅卷专家。学生书写也是评分的依据，你的任务是针对我提供的【学生英语作文】（图片形式），按照指定的维度进行深度批改，并输出一个严格符合格式要求的 JSON 数据。

# Input Data
- 学生身份：高中生
- 作文内容：图片中的手写文字（若有多张图片，请合并阅读）

# Task Requirements
请仔细阅读作文，进行多维度的分析，你需要完成以下 JSON 字段的填充：

1. **original_text**: 【OCR识别】准确识别图片中的手写英文，将所有图片内容合并为一段完整的文本。
2. **overall_evaluation**: 给出档次、总分、简短评语及四个维度的细分打分。
3. **highlights**: 分析内容、语言、结构三个方面的亮点。
4. **improvements**: 分析内容、语言、结构三个方面的待提升点。
5. **error_summary**: 总结出现的错误类型。
6. **detailed_errors**: 逐句列出具体错误、修正及解释。
7. **optimizations**: 选取表达平淡的句子进行升格润色。
8. **paragraph_reviews**: 分段点评。
9. **material_reuse_guide**: 一材多用分析。
10. **revised_text**: 【范文输出】基于原文，在吸纳上述所有修改建议后，输出一篇完整的、高质量的修正版作文。

# Output Format (JSON Schema)
请严格按照以下 JSON 结构输出，不要包含 markdown 代码块标记，直接输出纯文本 JSON 字符串。

{
  "original_text": "STRING: 识别到的作文原文（合并所有图片内容）",
  "overall_evaluation": {
    "tier": "STRING: 评定档次 (最好: 第五档, 最差: 第一档)",
    "total_score": "STRING: 总分（满分25分，5分为一个分界）",
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
  "revised_text": "STRING: 【此处输出最终的修正版范文】"
}
"""


# ==========================================
# 3. 功能函数
# ==========================================

def encode_image(image_path):
    """读取本地图片并转换为 Base64"""
    if not os.path.exists(image_path):
        print(f"⚠️ 警告: 找不到文件 {image_path}，已跳过")
        return None
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def grade_essay_multipage(image_path_list, prompt_text):
    """上传多张图片并获取 JSON 结果"""

    # --- A. 动态构建 content 列表 ---
    user_content_list = []

    print(f"🔄 正在读取 {len(image_path_list)} 张图片...")

    # 先循环处理每一张图片
    for img_path in image_path_list:
        base64_str = encode_image(img_path)
        if base64_str:
            user_content_list.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_str}"
                }
            })

    # 如果没有成功加载任何图片，直接返回
    if not user_content_list:
        print("⛔ 错误：没有有效的图片被加载。")
        return

    # 最后把文本提示词加进去
    user_content_list.append({
        "type": "text",
        "text": prompt_text
    })

    # --- B. 调用 API ---
    print(f"🚀 正在发送 {len(image_path_list)} 张图片给 Qwen-VL-Max (请耐心等待)...")

    try:
        completion = client.chat.completions.create(
            model="qwen-vl-max",
            messages=[
                {
                    "role": "system",
                    # 这里使用了上面定义的完整 SYSTEM_PROMPT
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_content_list
                },
            ],
            temperature=0.2,  # 降低随机性，保证 JSON 格式稳定
        )

        # 获取原始内容
        raw_content = completion.choices[0].message.content

        # 简单清洗 markdown 标记
        clean_content = raw_content.replace("```json", "").replace("```", "").strip()

        print("\n✅ === 批改结果 (JSON) ===\n")
        print(clean_content)

        return clean_content

    except Exception as e:
        print(f"💥 API 调用出错: {e}")
        return None


# ==========================================
# 4. 主程序入口
# ==========================================

if __name__ == "__main__":
    # =============================
    # 1. 命令行参数解析
    # =============================
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=str,
        default="qwen_essay_result.json",
        help="Qwen 批改结果 JSON 的输出路径",
    )
    parser.add_argument(
        "--images",
        nargs="+",
        help="作文图片路径列表（不传就用代码里写死的默认路径）",
    )
    args = parser.parse_args()

    # =============================
    # 2. 确定图片列表
    # =============================
    if args.images:
        # 如果通过命令行传了图片，就用命令行的
        my_images = args.images
    else:
        # 否则用你原来写死的那两张
        my_images = [
            r"G:\开发项目\AI_English\资料\中等\中等1-1.jpg",
            r"G:\开发项目\AI_English\资料\中等\中等1-2.jpg",
        ]

    # =============================
    # 3. 调用大模型批改
    # =============================
    result_json_str = grade_essay_multipage(
        my_images,
        "这是学生写的作文，共2页，请识别图片内容并严格按照 System Prompt 定义的 JSON 格式进行批改。",
    )

    # =============================
    # 4. 保存 JSON 到指定 --out
    # =============================
    if result_json_str:
        try:
            # 先尝试解析成 dict，确认是合法 JSON
            result_obj = json.loads(result_json_str)

            output_path = args.out  # ✅ 用 runner.py 传进来的路径

            # 确保输出目录存在（runs/时间戳/）
            out_dir = os.path.dirname(output_path)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result_obj, f, ensure_ascii=False, indent=2)

            print(f"\n💾 JSON 结果已保存到: {output_path}")
        except json.JSONDecodeError:
            # 如果解析失败，就把原始字符串另存为 .txt 方便排查
            print("⚠️ JSON 解析失败，已将原始内容保存为文本文件，方便你检查格式问题。")
            # raw 文件仍然放在同一目录下
            fallback_path = (args.out or "qwen_essay_result.json") + ".raw.txt"
            with open(fallback_path, "w", encoding="utf-8") as f:
                f.write(result_json_str)
            print(f"💾 原始内容保存到: {fallback_path}")
            # 非 0 退出码，方便 runner.py 掉用时检查失败
            raise
