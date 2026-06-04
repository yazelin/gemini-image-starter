# 繪圖魔法師入門:常見踩雷清單

用 AI 生圖時真的會踩到的坑,附上真實症狀與修法。引擎是 Google Gemini(`gemini-2.5-flash-image`),核心檔在 `app/prompt.py` 與 `app/gen.py`。

## 1. prompt 太籠統 → 結果不可控、每次都不一樣

這是最根本的坑,也是整個 repo 想解決的問題。Part 1(`part1_naive/naive.py`)只丟一句:

```python
PROMPT = "a cat"  # bare. no style, no lighting, no composition -> uncontrolled
```

症狀:跑出一張貓,但姿勢、畫風、背景、光線全是模型替你決定的。再跑一次,完全不同的一張。要拿來做產品(貼圖、頭像、角色)時,「每次都隨機」就是痛點。

為什麼:你沒說的每一個決定,模型都自己填。一句話 prompt 把所有控制權都讓出去了。

怎麼修:改用 Part 2 的結構化 prompt。`app/prompt.py` 的 `build_prompt` 把主體 / 風格 / 光線 / 構圖 / 配色 / 負面詞拆成命名欄位,同樣的輸入永遠產生同樣的描述:

```
a cat sitting by a window, style: ukiyo-e woodblock print, lighting: soft morning light, composition: centered, close-up, color palette: muted indigo and gold. Avoid: text, watermark, extra limbs
```

詳細對照見 `docs/08-prompt-engineering.md`。

## 2. 沒設 responseModalities → 拿不到圖

Gemini 的 `generateContent` 預設回的是文字。要它回圖,request body 必須明確要求 IMAGE 這個輸出模態。`app/gen.py` 的 `build_request_body` 已經設好:

```python
def build_request_body(prompt: str) -> dict:
    return {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }
```

症狀:漏掉 `generationConfig` 或把 `responseModalities` 拿掉,API 會回一個只有文字 part 的 candidate,於是下游 `extract_image` 抓不到 `inlineData`,丟出:

```
ValueError: no image found in response
```

怎麼修:確認 body 裡有 `"generationConfig": {"responseModalities": ["IMAGE"]}`。自己改 request 時最容易在這裡漏掉。

## 3. 沒處理「回傳沒有 image」的情況

就算你正確要求了圖,模型仍可能因為內容政策、prompt 被擋、或單純沒生成而回一個沒有 `inlineData` 的 candidate。如果你直接 `result["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]`,任何一層缺欄位都會丟難懂的 `KeyError` 或 `IndexError`。

`app/gen.py` 的 `extract_image` 用防禦式寫法,逐層 `.get()`,找不到圖就丟一個人看得懂的錯:

```python
def extract_image(result: dict) -> bytes:
    candidates = result.get("candidates", [])
    if candidates:
        for part in candidates[0].get("content", {}).get("parts", []):
            data = part.get("inlineData", {}).get("data")
            if data:
                return base64.b64decode(data)
    raise ValueError("no image found in response")
```

怎麼修:永遠假設回應「可能沒有圖」,用 `.get()` 一層層取、迴圈掃 parts(回應裡常常文字 part 和 image part 混在一起),最後給一個明確的 `ValueError`。`tests/test_request.py` 就驗證了「沒有 image 時要丟 ValueError」這條路徑。

## 4. 期待管理:生圖本來就不是「同一張」

結構化 prompt 讓你拿回控制權,但要講清楚它保證的是什麼:**同樣的欄位 → 同樣的「描述」→ 同一類、可控、可重現的畫面**,不是「位元組層級完全相同的同一張圖」。`demo_structured.py` 收尾印的就是這個語意:

```
saved structured_cat.png  (same fields -> same kind of picture, every time)
```

症狀:有人把「可重現」理解成「每次跑出一模一樣的 PNG」,然後因為兩次像素不同就以為壞了。

怎麼修:把可控性想成「你決定風格 / 光線 / 構圖 / 配色,並能說出要避免什麼」,而不是「凍結成單一檔案」。要更接近的話,把描述寫得更具體(見 `docs/08`);要真正鎖死同一張,那是另一個層次的需求(固定 seed / 存檔復用),不是這套入門的範圍。

## 5. 費用與額度

真正生圖要 `GEMINI_API_KEY`(免費申請:https://aistudio.google.com/apikey)。常見卡點:

- **沒設 key**:直接跑 `demo_structured.py` 或 `part1_naive/naive.py` 不會炸,但只會印提示、不生圖:
  ```
  (set GEMINI_API_KEY to actually generate: https://aistudio.google.com/apikey)
  ```
  把 key 設進環境變數再跑:`GEMINI_API_KEY=xxx uv run python demo_structured.py`。
- **免費額度有上限**:AI Studio 的免費層有每分鐘 / 每日請求數限制,連續猛生圖會碰到 429 之類的限流。寫批次或迴圈時要加節流與重試,別把額度一次燒光。
- **測試完全不需要 key**:`client_smoke_test.py` 跑的三支測試都不碰網路、不需 key(`test_gen_fake.py` 打的是本地假 server),所以驗證程式邏輯時不會花到任何額度。

## 6. 沒裝 uv,或忘了先 `uv sync`

本教學用 uv 管理環境,Ubuntu 與 Windows 共用同一套指令。兩個最常見的卡點:

- **沒裝 uv**:打 `uv ...` 直接 `command not found: uv`(Windows 是 `'uv' 不是內部或外部命令`)。先裝 uv,裝完重開終端機讓 PATH 生效,`uv --version` 印得出版本再繼續。
- **裝了 uv 但忘了先 `uv sync`**:先在 repo 根目錄跑一次 `uv sync`(建立 `.venv` 並安裝相依),之後 `uv run python demo_structured.py`、`uv run python client_smoke_test.py` 才會在對的環境裡跑。

完整流程:

```
git clone https://github.com/yazelin/gemini-image-starter.git
cd gemini-image-starter
uv sync
uv run python client_smoke_test.py
```

## Debug 順序

1. 先用 `uv run python client_smoke_test.py` 確認程式邏輯(prompt builder / 請求形狀 / build→POST→解析→存檔)全綠 —— 這步不需要 key、不碰網路。預期輸出:
   ```
   == tests/test_prompt.py ==
   OK: prompt builder test passed

   == tests/test_request.py ==
   OK: request/response shaping test passed

   == tests/test_gen_fake.py ==
   OK: gen against fake Gemini server passed

   OK: all checks passed
   ```
2. smoke 全綠後再接真 API:設 `GEMINI_API_KEY`,先跑 `part1_naive/naive.py` 確認 key 與網路通。
3. 拿不到圖時,先看是不是漏了 `responseModalities`(坑 2),再看回應裡到底有沒有 `inlineData`(坑 3)。
4. 結果不滿意、不可控,回去把 prompt 結構化、講具體(坑 1、`docs/08`)。
5. 連續生圖遇到限流,檢查免費額度與節流(坑 5)。

## 問別人前準備

- repo / branch
- 你打的完整指令與完整輸出(含完整錯誤訊息,別只貼最後一行)
- 你用的 prompt 字串(或 `build_prompt` 的各欄位)
- 是 smoke test(無 key)就壞,還是只有接真 API 才壞
- 你已經檢查過哪些設定(key 有沒有設、`responseModalities` 在不在)
