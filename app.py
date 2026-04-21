import os
import json
from flask import Flask, render_template, request, jsonify

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    import sympy as sp
except Exception:
    sp = None

app = Flask(__name__)

SYSTEM_PROMPT = """
You are a math tutor AI. Follow these rules strictly:
1. Answer in Traditional Chinese.
2. Solve the user's math problem step by step.
3. Do not skip important algebra steps.
4. If mode is beginner, explain each step in simple language.
5. If mode is exam, keep the explanation concise but still mathematically valid.
6. If the problem is statistics-related, include the formula used and explain why it applies.
7. End with a final answer section clearly labeled '最終答案'.
8. If the problem is ambiguous, state the assumption before solving.
9. If you are not certain, say so clearly.
10. Format math neatly with plaintext that can later be rendered by KaTeX or MathJax.
""".strip()


def build_user_prompt(question: str, mode: str, topic: str) -> str:
    mode_instruction = {
        "beginner": "請用初學者也看得懂的方式，詳細說明每一步。",
        "exam": "請用考試解題風格，精簡但完整地列出步驟。"
    }.get(mode, "請清楚解題。")

    topic_instruction = {
        "algebra": "題目類型偏向代數。",
        "calculus": "題目類型偏向微積分。",
        "statistics": "題目類型偏向統計。",
        "general": "題目類型可能混合。"
    }.get(topic, "題目類型可能混合。")

    return f"""
{mode_instruction}
{topic_instruction}

題目：
{question}
""".strip()


def ask_openai(question: str, mode: str, topic: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "目前尚未設定 OPENAI_API_KEY，所以系統先回傳示範答案格式。\n\n"
            "步驟一：辨識題型\n"
            "步驟二：套用對應公式\n"
            "步驟三：逐步化簡\n"
            "最終答案：請先在環境變數中設定 OPENAI_API_KEY 後再測試真實 AI 回答。"
        )

    if OpenAI is None:
        return "缺少 openai 套件，請先執行 pip install openai。"

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(question, mode, topic)}
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception:
      return (
        "（目前使用示範模式）\n\n"
        "題目理解：這是一題數學問題，系統將示範標準解題流程。\n\n"
        "解題步驟：\n"
        "1. 先辨識題目的類型。\n"
        "2. 找出適合使用的公式或方法。\n"
        "3. 依照步驟進行計算與整理。\n"
        "4. 檢查答案是否合理。\n\n"
        "最終答案：目前因 API 額度限制，這裡顯示示範解題格式。"
    )


def verify_expression(expr_str: str):
    if sp is None:
        return {"ok": False, "message": "SymPy 未安裝，無法驗證。"}
    try:
        expr = sp.sympify(expr_str)
        simplified = sp.simplify(expr)
        return {
            "ok": True,
            "message": f"化簡結果：{simplified}",
            "latex": sp.latex(simplified)
        }
    except Exception as e:
        return {"ok": False, "message": f"驗證失敗：{e}"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json(force=True)
    question = data.get("question", "").strip()
    mode = data.get("mode", "beginner")
    topic = data.get("topic", "general")

    if not question:
        return jsonify({"error": "請先輸入數學題目。"}), 400

    answer = ask_openai(question, mode, topic)
    return jsonify({"answer": answer})


@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json(force=True)
    expr = data.get("expression", "").strip()
    if not expr:
        return jsonify({"error": "請輸入要驗證的算式，例如 2*x + 3*x"}), 400
    result = verify_expression(expr)
    return jsonify(result)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
