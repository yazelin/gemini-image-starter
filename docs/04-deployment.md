# 用 AI 生圖入門:真正生圖與部署

前面的測試完全不需要 API key。但要**真的生出一張圖**,就得讓 client 連上真實的 Google Gemini 服務,這需要一把 `GEMINI_API_KEY`。這份文件帶你從拿 key 到存出第一張圖,最後談怎麼把它包成自己的小工具。

## 步驟 1:取得 GEMINI_API_KEY(免費)

到 [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey) 登入 Google 帳號,建立一把 API key。它是免費的。

拿到 key 後,設成環境變數。**不要把 key 寫進程式或 commit 進 git。**

Ubuntu / macOS:

```bash
export GEMINI_API_KEY="你的key"
```

Windows(PowerShell):

```powershell
$env:GEMINI_API_KEY = "你的key"
```

## 步驟 2:跑 Part 1,親眼看到「不可控」

先用一句話 prompt 生圖,感受痛點。`part1_naive/naive.py` 只送一句 `"a cat"`:

Ubuntu / macOS(可以一行帶 key 跑):

```bash
GEMINI_API_KEY=你的key uv run python part1_naive/naive.py
```

Windows(PowerShell,先 `export` 過就直接):

```powershell
uv run python part1_naive\naive.py
```

成功的話會存出 `naive_cat.png`,並印出:

```
saved naive_cat.png  (run again -> a different cat, every time)
```

**再跑一次。** 你會得到完全不同的一隻貓 —— 姿勢、畫風、背景、光線全變了。這就是 Part 1 要你看到的:一句話 prompt = 每次都隨機,做不了產品。

(沒設 key 時它會印 `set GEMINI_API_KEY first ...` 並結束,不會生圖。)

## 步驟 3:跑 Part 2,生出可控的圖

換成結構化 prompt。`demo_structured.py` 用 `build_prompt()` 把主體 / 風格 / 光線 / 構圖 / 配色 / 負面詞組成一條 prompt,再生圖:

```bash
uv run python demo_structured.py
```

設了 key 時,它會先印出 prompt,再存出 `structured_cat.png`:

```
prompt: a cat sitting by a window, style: ukiyo-e woodblock print, lighting: soft morning light, composition: centered, close-up, color palette: muted indigo and gold. Avoid: text, watermark, extra limbs
saved structured_cat.png  (same fields -> same kind of picture, every time)
```

成功的話你會看到:`structured_cat.png` 是一隻坐在窗邊、浮世繪木刻風、晨光柔和、置中近景、靛藍與金色調的貓,而且沒有文字 / 浮水印 / 多餘肢體(那是 `Avoid:` 擋掉的)。改 prompt 裡的欄位,成品就跟著你走 —— 這就是 Part 2 的可控、可重現。

> 圖片格式提醒:`save_image()` 直接把 Gemini 回傳的 bytes 寫成檔案,範例存成 `.png`。`.gitignore` 已經把 `*.png` 排除,所以生出來的圖不會誤 commit。

## 部署/分享前檢查

- 已跑過 `uv sync`,且 `uv run python client_smoke_test.py` 以 `OK: all checks passed` 收尾(免 key)。
- `GEMINI_API_KEY` 放在環境變數,**沒有**寫進任何檔案或 commit 進 git。
- 真正生圖前確認網路可連到 Google;測試則不需要網路。
- 生出的 `.png` 不要 commit(`.gitignore` 已處理,別自己 force-add)。

## key 安全筆記

- key 一律放環境變數或 secret manager,不要硬寫進程式、不要 commit。
- 如果懷疑 key 外洩,到 AI Studio 撤銷重發。
- 免費 key 有額度與速率限制;大量生圖前先看 Google 當前的配額說明。
- 公開 repo / CI 上不要放真 key —— 本 repo 的測試刻意設計成免 key,CI 用 `client_smoke_test.py` 就能把關。

## 想包成自己的小工具?

這個 starter 的兩塊(`build_prompt` + `generate`)已經夠你接著做產品。常見的下一步:

- **批次生圖**:把多組欄位放成一個清單,迴圈呼叫 `build_prompt()` + `generate()`,一次生一整套(例如同一角色的多種表情)。
- **填空式介面**:把「主體 / 風格 / 光線 / 構圖 / 配色 / 負面詞」做成表單,使用者填欄位、後端組 prompt。作者的 [PromptFill](https://github.com/yazelin/PromptFill) 就是這個概念的成品。
- **風格庫**:把常用的 `style` / `color` 預設存起來重複用,確保系列作風格一致。可以參考 [prompts-vault](https://mukiwu.github.io/prompts-vault/)(Nano Banana prompt 收集站)現成的高品質 prompt。
- **做成完整產品**:把生圖串進真正的應用。真實案例可以看 [line-sticker-studio](https://github.com/yazelin/line-sticker-studio)(LINE 貼圖製作)與 [catime](https://github.com/yazelin/catime)。

## 上線前實務提醒

把生圖放進正式服務前,至少要補:key 的安全保管與輪替、對 Gemini 呼叫的錯誤處理與重試(網路 / 配額 / 內容被擋)、生圖成本與速率控制、以及對使用者輸入(會變成 prompt)的基本檢查。這些不在最小 starter 範圍內,但都是把「能生一張圖」變成「能穩定服務很多人」的必修課。

想把這套改成你自己的產品、或談工作坊/顧問,寫信到 yazelin@ching-tech.com。
