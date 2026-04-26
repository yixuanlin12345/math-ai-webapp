const solveBtn = document.getElementById("solveBtn");
const verifyBtn = document.getElementById("verifyBtn");

solveBtn.addEventListener("click", async () => {
  const question = document.getElementById("question").value.trim();
  const mode = document.getElementById("mode").value;
  const topic = document.getElementById("topic").value;
  const result = document.getElementById("result");

  if (!question) {
    result.textContent = "請先輸入題目。";
    return;
  }

  solveBtn.disabled = true;
  solveBtn.textContent = "解題中...";
  result.textContent = "AI 正在解題中，請稍候...";

  try {
    const res = await fetch("/solve", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        question: question,
        mode: mode,
        topic: topic
      })
    });

    const data = await res.json();

    if (!res.ok) {
      result.textContent = data.error || "發生錯誤，請稍後再試。";
      return;
    }

    result.textContent = data.answer;
  } catch (err) {
    result.textContent = "系統錯誤：" + err.message;
  } finally {
    solveBtn.disabled = false;
    solveBtn.textContent = "開始解題";
  }
});

verifyBtn.addEventListener("click", async () => {
  const expression = document.getElementById("verifyInput").value.trim();
  const verifyResult = document.getElementById("verifyResult");

  if (!expression) {
    verifyResult.textContent = "請先輸入算式。";
    return;
  }

  verifyBtn.disabled = true;
  verifyBtn.textContent = "驗證中...";
  verifyResult.textContent = "SymPy 正在驗證中，請稍候...";

  try {
    const res = await fetch("/verify", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        expression: expression
      })
    });

    const data = await res.json();

    if (!res.ok) {
      verifyResult.textContent = data.error || "發生錯誤，請稍後再試。";
      return;
    }

    if (data.latex) {
      verifyResult.textContent = data.message + "\nLaTeX: " + data.latex;
    } else {
      verifyResult.textContent = data.message;
    }
  } catch (err) {
    verifyResult.textContent = "系統錯誤：" + err.message;
  } finally {
    verifyBtn.disabled = false;
    verifyBtn.textContent = "驗證";
  }
});