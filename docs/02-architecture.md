# 用 AI 生圖入門:架構說明

整個 repo 的設計只圍繞一個觀念:**把「想畫什麼」(prompt 設計)和「怎麼送出去生圖」(API client)拆開,再讓兩者都能在沒有 key、沒有網路的情況下測試。**

## 核心檔案

- `app/prompt.py`:結構化 prompt builder。`build_prompt()` 把主體 / 風格 / 光線 / 構圖 / 配色 / 負面詞組成一條 prompt 字串。**純函式**,沒有網路、沒有 key。
- `app/gen.py`:最小 Gemini 生圖 client。`build_request_body()` / `extract_image()` 是純函式;`generate()` 真的打 HTTP;`save_image()` 存檔。
- `part1_naive/naive.py`:Part 1 baseline,一句 `"a cat"`,展示「不可控」的痛點。
- `demo_structured.py`:Part 2 示範,用 `build_prompt()` 組結構化 prompt 再生圖。
- `tests/fake_gemini.py`:本地假 Gemini server,回 Gemini 形狀的固定 1x1 PNG,讓 client 路徑免 key 跑完整流程。
- `tests/test_prompt.py` / `tests/test_request.py` / `tests/test_gen_fake.py`:三個確定性測試。
- `client_smoke_test.py`:一次跑完上面三個測試。

## 三塊各做一件事

### 1. prompt builder(純函式,可重現)

`build_prompt()` 收一個必填的 `subject`,加上一堆選填的具名欄位(`style` / `lighting` / `composition` / `color` / `extra` / `negative`),依固定順序拼成一條字串:有填的欄位才出現,`negative` 變成結尾的 `. Avoid: ...` 子句。

它**完全沒有副作用**:不連網、不讀 key、不存檔。所以「同樣的輸入永遠回同樣的字串」—— 這正是 Part 2 相對 Part 1 的關鍵差異(可控、可重現),也讓它可以用純粹的字串斷言來測。

這一塊就是「繪圖魔法師」的核心魔法:**把每個會影響成品的決定,從模型手裡拿回到你的 prompt 裡。**

### 2. gen client(對齊真實 Gemini API 形狀)

`app/gen.py` 刻意對齊真實 Google Gemini 的生圖 API:

```
POST {base_url}/{model}:generateContent?key={api_key}
body: {"contents":[{"parts":[{"text": prompt}]}],
       "generationConfig":{"responseModalities":["IMAGE"]}}
resp: candidates[0].content.parts[].inlineData.data  (base64 image)
```

它拆成三個函式:

- `build_request_body(prompt)` — 純函式,把 prompt 包成上面的 body。
- `extract_image(result)` — 純函式,從回應裡找第一個 `inlineData.data`,base64 解碼成圖片 bytes;找不到就丟 `ValueError`。
- `generate(prompt, api_key, *, model, base_url, timeout)` — 真的用 `httpx.post` 打出去,把上面兩個純函式串起來。

**關鍵設計:`base_url` 可注入。** 預設指向真實 Google 服務(`https://generativelanguage.googleapis.com/v1beta/models`),但測試可以把它指向本地假 server。**同一份 client 程式,既打真服務、也能離線測。**

### 3. 假 server(讓整條路徑可測)

`tests/fake_gemini.py` 是一個用 Python 標準函式庫寫的迷你 HTTP server。它對任何 POST 都回一個 Gemini 形狀的回應,`inlineData.data` 是一張固定的 1x1 PNG。`start()` 在隨機 port 起 server,回傳 `(server, base_url)`。

有了它,`test_gen_fake.py` 就能把 `generate()` 的 `base_url` 指向這個假 server,真的跑完整路徑:build body → POST → 解析 `inlineData` → base64 解碼 → 存檔 → 讀回比對。**全程沒有真實 API key、沒有外網。**

## 資料流(Part 2 真實生圖時)

1. 你呼叫 `build_prompt(subject, style=..., lighting=..., ...)` → 拿到一條結構化 prompt 字串。
2. `generate(prompt, key)` 內部呼叫 `build_request_body(prompt)` 組出 Gemini body。
3. `httpx.post` 把 body POST 到 `{base_url}/{model}:generateContent?key={key}`。
4. Gemini 回 `candidates[0].content.parts[].inlineData.data`(base64 圖片)。
5. `extract_image()` 找出第一個 `inlineData.data`、base64 解碼成 bytes。
6. `save_image(bytes, path)` 寫成 `.png`。

測試時,第 3 步的 `base_url` 換成假 server,其餘完全一樣 —— 這就是為什麼測試能涵蓋真實路徑卻不需要 key。

## 設計原則

- **prompt 設計和 API client 分開** — 一塊管「畫什麼」、一塊管「怎麼送」,各自獨立、各自可測。
- **純函式優先** — `build_prompt` / `build_request_body` / `extract_image` 都沒有副作用,所以好懂、好測、結果可重現。
- **可注入的邊界** — `base_url`(以及 `model`、`timeout`)是參數,讓同一份程式能在真服務與假 server 之間切換。
- **key 只在真正生圖時才需要** — 學習與測試完全免 key、免網路。
- 範例程式刻意保持小,方便你看懂後改成自己的版本。
