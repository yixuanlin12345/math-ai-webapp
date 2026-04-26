import os
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
你是一個數學老師，請遵守以下規則：
1. 使用繁體中文回答。
2. 逐步解數學題。
3. 不要跳過重要代數步驟。
4. 如果是 beginner 模式，要用初學者看得懂的方式解釋。
5. 如果是 exam 模式，要用考試作答風格，精簡但完整。
6. 如果是統計題，要寫出公式並解釋為什麼使用。
7. 最後一定要有「最終答案」。
""".strip()


def build_user_prompt(question, mode, topic):
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


def ask_openai(question, mode, topic):
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        return (
            "目前尚未設定 OPENROUTER_API_KEY。\n\n"
            "請先在環境變數中設定 OPENROUTER_API_KEY 後再測試真實 AI 回答。\n\n"
            "最終答案：目前無法連接 AI，因為尚未設定 API Key。"
        )

    if OpenAI is None:
        return "缺少 openai 套件，請先執行：pip install openai"

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

        response = client.chat.completions.create(
            model="openrouter/auto",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(question, mode, topic)}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"錯誤：{str(e)}"


def verify_expression(expr_str):
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
