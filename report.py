import json
import re
from datetime import datetime
from pathlib import Path
from fpdf import FPDF

# ==========================================
# 辅助函数：强制换行
# ==========================================
def _force_wrap_text(text, max_word_length=50):
    """强制打断超长字符串以允许换行，防止PDF生成崩溃。"""
    if not isinstance(text, str):
        return str(text)
    
    wrapped_words = []
    for word in text.split(' '):
        if len(word) > max_word_length:
            # 使用正则表达式将长单词切片
            wrapped_word = ' '.join(re.findall(f'.{{1,{max_word_length}}}', word))
            wrapped_words.append(wrapped_word)
        else:
            wrapped_words.append(word)
    return ' '.join(wrapped_words)

# ==========================================
# PDF 生成类 (已增强)
# ==========================================
class EssayPDF(FPDF):
    def __init__(self, font_path: Path):
        super().__init__()
        self.add_page()
        self.add_font("NotoSans", "", font_path, uni=True)
        self.add_font("NotoSans", "B", font_path, uni=True)
        self.set_auto_page_break(auto=True, margin=15)
        self.set_font("NotoSans", "", 12)

    def add_title(self, text):
        self.set_font("NotoSans", "B", 20)
        self.cell(0, 12, txt=text, ln=True, align="C")
        self.ln(4)
        self.set_font("NotoSans", "", 12)

    def add_section(self, title, content, size=12):
        self.set_font("NotoSans", "B", size)
        self.cell(0, 8, txt=title, ln=True)
        self.set_font("NotoSans", "", size - 1)
        # 安全处理：在渲染前强制换行
        safe_content = _force_wrap_text(content)
        self.multi_cell(0, 7, txt=safe_content)
        self.ln(2)

    def add_kv_block(self, title, kv_dict):
        self.set_font("NotoSans", "B", 12)
        self.cell(0, 8, txt=title, ln=True)
        self.set_font("NotoSans", "", 11)
        for k, v in kv_dict.items():
            self.cell(0, 6, txt=f"{k}: {v}", ln=True)
        self.ln(2)

    def add_list_block(self, title, items):
        self.set_font("NotoSans", "B", 12)
        self.cell(0, 8, txt=title, ln=True)
        self.set_font("NotoSans", "", 11)
        for it in items:
            if isinstance(it, dict):
                line = " - " + it.get("point", "")
                # 安全处理
                self.multi_cell(0, 6, txt=_force_wrap_text(line))
                if "evidence" in it:
                    evidence_line = "   证据: " + it["evidence"]
                    # 安全处理
                    self.multi_cell(0, 6, txt=_force_wrap_text(evidence_line))
            else:
                # 安全处理
                self.multi_cell(0, 6, txt=" - " + _force_wrap_text(str(it)))
        self.ln(2)

# ==========================================
# 主构建函数
# ==========================================
def build_pdf(data, pdf_path="essay_report.pdf", font_path="NotoSansSC-Regular.otf"):
    font_path = Path(font_path)
    pdf = EssayPDF(font_path=font_path)

    pdf.add_title("英语作文深度评估报告")
    pdf.set_font("NotoSans", "", 10)
    pdf.cell(0, 6, f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(4)

    pdf.add_section("原文", data.get("original_text", ""))
    overall = data.get("overall_evaluation", {})
    pdf.add_section("总评", overall.get("brief_comment", ""))
    pdf.add_kv_block("评分", {
        "等级": overall.get("tier", ""),
        "总分": overall.get("total_score", ""),
        **overall.get("score_breakdown", {})
    })

    highlights = data.get("highlights", {})
    for cat, items in highlights.items():
        pdf.add_list_block(f"亮点 - {cat}", items)

    improvements = data.get("improvements", {})
    for cat, items in improvements.items():
        pdf.add_list_block(f"改进 - {cat}", items)

    errors = data.get("error_summary", {})
    for cat, items in errors.items():
        pdf.add_list_block(f"错误 - {cat}", items)

    detailed = data.get("detailed_errors", [])
    pdf.add_list_block("详细错误", [
        f"[{e.get('type', 'N/A')}] {e.get('original_sentence', '')} -> {e.get('correction', '')} ({e.get('explanation','')})"
        for e in detailed
    ])

    opts = data.get("optimizations", [])
    pdf.add_list_block("表达升格", [
        f"{o.get('original_sentence', '')} -> {o.get('correction', '')} ({o.get('explanation','')})"
        for o in opts
    ])

    para = data.get("paragraph_reviews", [])
    pdf.add_list_block("段落点评", [
        f"第{p.get('paragraph_index', 'N/A')}段: {p.get('summary', '')} | 问题: {p.get('issues','')}"
        for p in para
    ])

    reuse = data.get("material_reuse_guide", {})
    pdf.add_list_block("素材复用 - 主题", reuse.get("applicable_themes", []))
    pdf.add_section("素材复用 - 方向", reuse.get("processing_direction", ""))
    pdf.add_section("素材复用 - 拓展", reuse.get("expansion_ideas", ""))

    pdf.add_section("高分范文", data.get("revised_text", ""))

    pdf.output(pdf_path)
    print(f"PDF saved to {pdf_path}")

if __name__ == "__main__":
    # 这是一个示例，你需要确保 qwen_essay_result.json 存在才能运行此脚本
    try:
        with open("qwen_essay_result.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        build_pdf(data, pdf_path="essay_report.pdf", font_path="NotoSansSC-Regular.otf")
    except FileNotFoundError:
        print("错误: 未找到 qwen_essay_result.json。请先生成一个结果文件。")
