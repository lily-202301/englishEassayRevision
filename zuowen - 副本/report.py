import json
from datetime import datetime
from pathlib import Path
from fpdf import FPDF

# 可替换为你自己的 Qwen 调用逻辑
def fetch_qwen_result():
    """如果你已有 qwen_essay_result.json，直接加载即可；否则在这里调用 Qwen API 返回同结构的 dict。"""
    with open("qwen_essay_result.json", "r", encoding="utf-8") as f:
        return json.load(f)

class EssayPDF(FPDF):
    def __init__(self, font_path: Path):
        super().__init__()
        self.add_page()
        # 注册字体（中文需要）
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
        self.multi_cell(0, 7, txt=content)
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
            # item 可以是 str，或带 point/evidence 的 dict
            if isinstance(it, dict):
                line = " - " + it.get("point", "")
                self.multi_cell(0, 6, txt=line)
                if "evidence" in it:
                    self.multi_cell(0, 6, txt="   证据: " + it["evidence"])
            else:
                self.multi_cell(0, 6, txt=" - " + str(it))
        self.ln(2)

def build_pdf(data, pdf_path="essay_report.pdf", font_path="NotoSansSC-Regular.ttf"):
    font_path = Path(font_path)
    pdf = EssayPDF(font_path=font_path)

    # 顶部标题与日期
    pdf.add_title("英语作文深度评估报告")
    pdf.set_font("NotoSans", "", 10)
    pdf.cell(0, 6, f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(4)

    pdf.add_section("原文", data["original_text"])
    overall = data.get("overall_evaluation", {})
    pdf.add_section("总评", overall.get("brief_comment", ""))
    pdf.add_kv_block("评分", {
        "等级": overall.get("tier", ""),
        "总分": overall.get("total_score", ""),
        **overall.get("score_breakdown", {})
    })

    # 亮点、改进
    highlights = data.get("highlights", {})
    for cat, items in highlights.items():
        pdf.add_list_block(f"亮点 - {cat}", items)

    improvements = data.get("improvements", {})
    for cat, items in improvements.items():
        pdf.add_list_block(f"改进 - {cat}", items)

    # 错误汇总
    errors = data.get("error_summary", {})
    for cat, items in errors.items():
        pdf.add_list_block(f"错误 - {cat}", items)

    # 详细错误
    detailed = data.get("detailed_errors", [])
    pdf.add_list_block("详细错误", [
        f"[{e['type']}] {e['original_sentence']} -> {e['correction']} （{e.get('explanation','')}）"
        for e in detailed
    ])

    # 升级建议
    opts = data.get("optimizations", [])
    pdf.add_list_block("表达升格", [
        f"{o['original_sentence']} -> {o['correction']} （{o.get('explanation','')}）"
        for o in opts
    ])

    # 段落点评
    para = data.get("paragraph_reviews", [])
    pdf.add_list_block("段落点评", [
        f"第{p['paragraph_index']}段: {p['summary']} | 问题: {p.get('issues','')}"
        for p in para
    ])

    # 素材复用
    reuse = data.get("material_reuse_guide", {})
    pdf.add_list_block("素材复用 - 主题", reuse.get("applicable_themes", []))
    pdf.add_section("素材复用 - 方向", reuse.get("processing_direction", ""))
    pdf.add_section("素材复用 - 拓展", reuse.get("expansion_ideas", ""))

    # 高分范文
    pdf.add_section("高分范文", data.get("revised_text", ""))

    pdf.output(pdf_path)
    print(f"PDF saved to {pdf_path}")

if __name__ == "__main__":
    data = fetch_qwen_result()
    build_pdf(data, pdf_path="essay_report.pdf", font_path="NotoSansSC-Regular.ttf")
