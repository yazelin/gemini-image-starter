# AI 生圖入門 · 繪圖魔法師 CI Design

> English name: Gemini Image Starter

## 定位

**主要受眾:** 第一次用 AI 生圖、想學會「讓結果可控」的人,以及想把生圖接進自家流程的開發者。
**核心承諾:** 從一句話 prompt(每次都不一樣)走到結構化 prompt(可控、可重現),看懂核心魔法是 prompt 設計。
**痛點切入:** 不是「會不會用工具」的問題 ——「a cat」每次生出來都不一樣,要做產品(貼圖、頭像、角色)時這種隨機就是痛點。
**類別提示:** Gemini / structured prompt / 可重現
**系列定位:** 「繪圖魔法師」系列的基礎/前置模組。引擎用 Google Gemini(`gemini-2.5-flash-image`)。

## 設計理念

### 1. prompt 設計是核心魔法

整個範本要傳達的一件事:讓 AI 生圖可控的,不是某個按鈕或某個模型參數,而是 prompt 設計。所以 `app/prompt.py` 是整個 Part 2 的核心 —— 它把「主體 / 風格 / 光線 / 構圖 / 配色 / 額外 / 負面詞」變成具名欄位,組成一個結構化字串。它是純函式:沒有網路、沒有 API key,同樣的輸入永遠產生同樣的字串,所以又好懂又好測。

### 2. naive → structured 的對照敘事

- **Part 1(baseline,`part1_naive/naive.py`):** 一句 `"a cat"`。刻意保持天真,讓學習者親眼看到「每次都不一樣」—— 姿勢、畫風、背景、光線全是模型替你決定的。這是被製造出來的痛點。
- **Part 2(`demo_structured.py` + `app/prompt.py`):** 同一隻貓,改用結構化 prompt 把每個決定具名化。同樣的欄位 → 同樣的描述 → 可控、可重現。

兩支 demo 共用同一個 `app/gen.py`,差別只在 prompt,把「魔法在 prompt、不在 client」這件事用程式碼直接演出來。

### 3. gen client 對齊真實 API + 可注入 base_url 做免-key 測試

`app/gen.py` 是對齊真實 Google Gemini image API 的最小 client:

```
POST {base_url}/{model}:generateContent?key={api_key}
body: {"contents":[{"parts":[{"text": prompt}]}],
       "generationConfig":{"responseModalities":["IMAGE"]}}
resp: candidates[0].content.parts[].inlineData.data   (base64)
```

關鍵設計是把 `base_url` 做成可注入參數。真正生圖時用預設的 Gemini endpoint;測試時把 `base_url` 指向 `tests/fake_gemini.py`(一個回固定 1x1 PNG 的本地假 server),於是同一條 client 路徑(build body → POST → 解析 inlineData → 解碼 → 存檔)能在沒有 API key、沒有外部網路的情況下端到端跑完。

請求/回應的形狀也拆成純函式(`build_request_body`、`extract_image`),讓「形狀對不對」可以離線斷言,跟「真的有沒有打到 API」分開測。

### 4. 確定性測試先於燒額度

三組測試全部免 key、免網路:`test_prompt.py`(prompt builder)、`test_request.py`(請求/回應形狀)、`test_gen_fake.py`(對本地假 server 跑完整路徑)。`client_smoke_test.py` 一次跑完。學習者先把邏輯勾正確,再拿免費 key 去真的生圖,不浪費額度。

## 視覺識別

- **主色:** `#f472b6`
- **輔色:** `#be185d`
- **背景:** `#1a0a16`
- **語言策略:** 繁體中文為主,英文產品名作為輔助與 SEO。
- **風格:** dark developer-tool landing page、技術網格、洋紅高對比 CTA、明確產品 glyph。

## Landing Page CTA

主要 CTA:**收到更新 / 小班開課通知**(email 名單)。
Landing 專心收名單:只放 hero、解決什麼、email 表單(`id="waitlist"`)、關於作者、從範本到正式產品 —— 不放延伸資源/外部連結卡(跟家族一致)。
表單用 MailerLite embedded(`data-form` 先放 placeholder),Universal JS 先整段註解掛起,等接上真實 form id 再啟用;在此之前有一行 fallback「來信 yazelin@ching-tech.com」。

## 功能賣點

- Part 1 一句話 prompt baseline,看清「每次都不一樣」的痛點
- Part 2 結構化 prompt(主體 / 風格 / 光線 / 構圖 / 配色 / 負面詞)→ 可控、可重現
- 核心魔法是 prompt 設計,不是某個按鈕
- gen client 對齊真實 Gemini API,`base_url` 可注入
- 免 API key 的確定性測試:先勾邏輯,再燒額度

## Assets

- `assets/banner.svg`:README / Open Graph / hero banner
- `assets/logo.svg`:square product mark
- `index.html`:繁中 GitHub Pages CTA landing page
