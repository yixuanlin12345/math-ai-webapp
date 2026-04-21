# AI 數學解題與教學輔助系統

## 專題簡介
這是一個以 Flask 建立的 AI 數學解題網站，支援：
- 使用者輸入數學題目
- Beginner / Exam 兩種解題模式
- 題型分類：代數、微積分、統計
- 使用 SymPy 驗證與化簡算式

## 安裝方式
```bash
pip install -r requirements.txt
```

## 設定 API Key
macOS / Linux:
```bash
export OPENAI_API_KEY="你的金鑰"
```

Windows PowerShell:
```powershell
setx OPENAI_API_KEY "你的金鑰"
```

## 啟動
```bash
python app.py
```

## 專題亮點
1. AI 步驟式解題
2. Prompt Engineering 模式切換
3. SymPy 驗證，提高可靠性
4. 可延伸為作品集專題
