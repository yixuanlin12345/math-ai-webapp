const solveBtn = document.getElementById('solveBtn');
const verifyBtn = document.getElementById('verifyBtn');

solveBtn.addEventListener('click', async () => {
  const question = document.getElementById('question').value.trim();
  const mode = document.getElementById('mode').value;
  const topic = document.getElementById('topic').value;
  const result = document.getElementById('result');

  if (!question) {
    result.textContent = '請先輸入題目。';
    return;
  }

  result.textContent = '解題中...';

  try {
    const res = await fetch('/solve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, mode, topic })
    });

    const data = await res.json();
    if (!res.ok) {
      result.textContent = data.error || '發生錯誤';
      return;
    }
    result.textContent = data.answer;
  } catch (err) {
    result.textContent = '系統錯誤：' + err.message;
  }
});

verifyBtn.addEventListener('click', async () => {
  const expression = document.getElementById('verifyInput').value.trim();
  const verifyResult = document.getElementById('verifyResult');

  if (!expression) {
    verifyResult.textContent = '請先輸入算式。';
    return;
  }

  verifyResult.textContent = '驗證中...';

  try {
    const res = await fetch('/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ expression })
    });

    const data = await res.json();
    if (!res.ok) {
      verifyResult.textContent = data.error || '發生錯誤';
      return;
    }
    verifyResult.textContent = data.message + (data.latex ? '\nLaTeX: ' + data.latex : '');
  } catch (err) {
    verifyResult.textContent = '系統錯誤：' + err.message;
  }
});
