# 用 AI 生圖入門:快速開始

這份文件帶你「不卡住、走完一遍、知道自己成功了」。每一步都有:要打的指令 → 跑完的真實輸出 → 成功的話你會看到什麼。

**好消息:跑完整套測試完全不需要 API key、也不需要連網。** 真正生圖才需要 key,那留到 `04-deployment.md`。

## 前置需求

- Python 3.11+
- Git
- 會用終端機
- [uv](https://docs.astral.sh/uv/)(本教學的環境管理工具)

### 安裝 uv(一次就好)

Ubuntu / macOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows(PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

裝完重開終端機,`uv --version` 印得出版本就 OK。`uv sync` 會依 `pyproject.toml` + `uv.lock` 自動建立 `.venv` 並裝好套件(毋須手動 venv / activate),`uv run` 直接在那個環境裡執行。**以下 `uv sync` / `uv run` 在 Ubuntu 與 Windows 完全相同。**

這個 starter 只依賴一個第三方套件(`httpx`,用來打 HTTP),測試用的假 server 則完全用 Python 標準函式庫。

## 這個 repo 是什麼(先讀一句)

它教你「用 AI 生圖」:Part 1 用一句話 prompt 生圖讓你看到「每次都不一樣」的痛點;Part 2 用結構化 prompt 把控制權拿回來。引擎是 Google Gemini 的 `gemini-2.5-flash-image`。

## 步驟 1:取得程式

實際指令:

```bash
git clone https://github.com/yazelin/gemini-image-starter.git
cd gemini-image-starter
uv sync
```

成功的話你會看到:clone 完成,`ls` 看得到 `app/`、`part1_naive/`、`demo_structured.py`、`client_smoke_test.py`、`tests/`,而 `uv sync` 印出類似下面的訊息(會建立 `.venv` 並裝好 `httpx`):

```
Using CPython 3.11.13
Creating virtual environment at: .venv
Resolved 2 packages in 1ms
Installed 1 package in 3ms
 + httpx==0.27.0
```

(實際版本號與套件數會隨環境略有不同,重點是有建出 `.venv` 且沒有錯誤。)

## 步驟 2:跑 smoke test(最快的驗證,免 key)

`client_smoke_test.py` 會依序跑三個確定性測試:prompt builder 的純函式、Gemini 請求/回應的形狀、以及對一個**本地假 Gemini server** 跑完整的「build body → POST → 解析 base64 → 存檔」流程。全程不需要 API key、不需要連網。

實際指令:

```bash
uv run python client_smoke_test.py
```

真實輸出(這是實際跑出來的,不是示意):

```
== tests/test_prompt.py ==
OK: prompt builder test passed

== tests/test_request.py ==
OK: request/response shaping test passed

== tests/test_gen_fake.py ==
OK: gen against fake Gemini server passed

OK: all checks passed
```

成功的話你會看到:三段 `OK: ...`,最後一行是 `OK: all checks passed`。

- `test_prompt.py` 驗證**結構化 prompt builder**:同樣的輸入永遠回同樣的字串(這就是「可重現」),而且只給主體時就只回主體。
- `test_request.py` 驗證**請求/回應形狀**:prompt 包進 Gemini 的 `contents[].parts[].text` + `generationConfig.responseModalities:["IMAGE"]`,並能從回應的 `inlineData.data`(base64)解回圖片 bytes。
- `test_gen_fake.py` 把上面兩件事串起來,對**本地假 server** 跑完整 client 路徑:送出 prompt、收到 Gemini 形狀的回應、解出 1x1 PNG、存檔、再讀回來比對。

只要看到 `OK: all checks passed`,就代表 prompt 設計、API 形狀、整條生圖流程在你機器上都跑通了 —— **而且這一切都不需要 key。**

## 步驟 3:看一眼結構化 prompt 長什麼樣(免 key)

`demo_structured.py` 把「主體 / 風格 / 光線 / 構圖 / 配色 / 負面詞」組成一條 prompt 並印出來。沒設 `GEMINI_API_KEY` 時它**只印 prompt、不生圖**,所以你現在就能跑、看清楚結構化 prompt 的樣子。

實際指令:

```bash
uv run python demo_structured.py
```

真實輸出:

```
prompt: a cat sitting by a window, style: ukiyo-e woodblock print, lighting: soft morning light, composition: centered, close-up, color palette: muted indigo and gold. Avoid: text, watermark, extra limbs
(set GEMINI_API_KEY to actually generate: https://aistudio.google.com/apikey)
```

成功的話你會看到:一條把每個決定都寫清楚的 prompt(主體、`style:`、`lighting:`、`composition:`、`color palette:`,最後 `Avoid:` 列出不要的東西),以及一句提示「設了 key 才會真的生圖」。

對照 Part 1 的一句話 `"a cat"`:差別一眼就看得出來 —— **每個會影響成品的決定,在這裡都被你寫進去了。** 這就是 Part 2 的核心。

## 第一次成功的標準(整體確認)

跑完上面三步,你應該能勾掉這份清單:

- [ ] `uv sync` 建好 `.venv`、沒有錯誤。
- [ ] `uv run python client_smoke_test.py` 印出三段 `OK:` 並以 `OK: all checks passed` 收尾。
- [ ] `uv run python demo_structured.py` 印出那條結構化 prompt。
- [ ] 全程沒用到任何 API key、也沒連外。

接著看 `02-architecture.md` 理解這三塊怎麼分工,或直接跳到 `03-step-by-step.md` 親手做一遍。想真正生出圖片(需要 key),看 `04-deployment.md`。
