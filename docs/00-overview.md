# 用 AI 生圖入門：總覽

用最小的 Google Gemini 生圖 client，看懂「為什麼一句話 prompt 不可控」，再學會用**結構化 prompt** 把控制權拿回來。這是「繪圖魔法師」系列的基礎/前置模組:先把第一個魔法 —— **prompt 設計** —— 打穩。

## 兩段:先看痛點、再學魔法

這份教材分兩段:

- **Part 1(baseline,`part1_naive/naive.py`)** — 用最天真的方式生圖:一句 `"a cat"` 丟給 Gemini。會生出一張貓,但**每次都不一樣**:姿勢、畫風、背景、光線全是模型替你決定的。這就是痛點。
- **Part 2(`app/prompt.py` + `app/gen.py` + `demo_structured.py`)** — 用**結構化 prompt**(主體 / 風格 / 光線 / 構圖 / 配色 / 負面詞)把這些決定權拿回來:同樣的輸入 → 同樣的描述 → 可控、可重現。

先親眼看到「一句話 = 隨機」,再體會「結構化 = 可控」。核心魔法不在 API,而在 **prompt 怎麼寫**。

## 適合誰

想用 AI 生圖、但受不了「每次結果都不一樣」的人;想把生圖做成產品(貼圖、頭像、角色、素材)的開發者與創作者。

## 你會做出什麼

- 一個純函式的**結構化 prompt builder**(主體 / 風格 / 光線 / 構圖 / 配色 / 負面詞 → 一條 prompt 字串)
- 一個對齊真實 Gemini API 形狀的**最小生圖 client**(build body → POST → 解析 base64 → 存圖)
- 一組**免 API key 的確定性測試**(prompt 純函式 + 請求/回應形狀 + 對本地假 server 跑完整流程)
- 真的拿到 `GEMINI_API_KEY` 後,跑出第一張可控的圖

## 兩個關鍵設計(先記一句)

1. **prompt builder 是純函式** — 沒有網路、沒有 API key,同樣的輸入永遠回同樣的字串,所以完全可測、可重現。
2. **gen client 對齊真實 Gemini,但 `base_url` 可注入** — 同一份程式可以打真實 Google 服務,也可以在測試裡指向本地假 server。**所以測試完全不需要 key、不需要連網。**

## 建議學習方式

1. 先照 `01-quickstart.md` 跑起來(免 key,只跑測試,確認環境 OK)。
2. 再看 `02-architecture.md` 理解三塊:prompt builder(純函式)+ gen client(對齊真實 Gemini)+ 假 server(可測)。
3. 照 `03-step-by-step.md` 從零做出 prompt builder + gen client + 測試,每步可動手。
4. 想真正生圖時看 `04-deployment.md`(取得 key、跑 Part 1 與 Part 2、存圖、包成小工具)。

## 免費與付費怎麼分

這個 repo 公開最小可跑版本與完整教學。真正適合工作坊或顧問的部分,是陪你把 prompt 設計、風格庫、生圖流程改成你自己的產品。

- 免費:可重現的 starter、教學文件、結構化 prompt 設計觀念。
- 付費工作坊:手把手帶你設計自己的 prompt 結構、建風格庫、把生圖串成流程。
- 企業顧問:需求訪談、PoC、把 AI 生圖落地成內部工具或產品。

## 延伸資源

學會結構化 prompt 之後,作者自己也做了幾個生圖周邊可以接著玩:

- [PromptFill](https://github.com/yazelin/PromptFill) — 結構化提示詞工具,把「主體 / 風格 / 光線……」這套填空式 prompt 變成可操作介面。
- [prompts-vault](https://github.com/yazelin/prompts-vault) — Nano Banana prompt 收集站,現成可抄的高品質 prompt。

把生圖做成真正的產品長什麼樣,可以看這兩個真實案例:

- [line-sticker-studio](https://github.com/yazelin/line-sticker-studio) — 把生圖做成 LINE 貼圖製作工具。
- [catime](https://github.com/yazelin/catime) — 生圖驅動的實際作品。

有問題或想談工作坊/顧問,寫信到 yazelin@ching-tech.com。
