# 繪圖魔法師入門:prompt 設計(對照課)

前面你已經跑過兩種寫法:Part 1 一句話 prompt(`part1_naive/naive.py`),Part 2 結構化 prompt(`app/prompt.py` + `demo_structured.py`)。這一課把兩者並排,讓你親眼看到「同樣是生圖,差別全在 prompt 怎麼寫」。

引擎兩邊完全一樣(`gemini-2.5-flash-image`,同一個 `app/gen.py`),唯一不同的是丟進去的那段文字。**核心魔法不是模型,是 prompt 設計。**

## 先講結論:差在哪

| 面向 | Part 1 一句話(`naive.py`) | Part 2 結構化(`build_prompt`) |
|---|---|---|
| prompt 內容 | `"a cat"` | 主體 + style + lighting + composition + color + negative |
| 誰做決定 | 模型自己填滿所有未說的細節 | 你逐項指定,只把沒指定的留給模型 |
| 可控性 | 低 —— 姿勢 / 畫風 / 背景 / 光線都隨機 | 高 —— 風格 / 光線 / 構圖 / 配色都你說了算 |
| 可重現性 | 每次都不一樣 | 同欄位 → 同描述 → 同一類畫面 |
| 能否「說要避免什麼」 | 不能 | 能(`negative` → `Avoid: ...`) |
| 拿來做產品 | 痛點(每次隨機,系列做不齊) | 可行(整套貼圖 / 一系列角色穩定產出) |

兩條核心訊息:

1. **一句話 prompt 把控制權全讓給模型。** 你沒說的每一個決定,它都自己填,所以每次都不一樣。
2. **結構化 prompt 把控制權拿回來。** 把主體 / 風格 / 光線 / 構圖 / 配色 / 負面詞拆成命名欄位,同樣的輸入永遠描述同樣的畫面。

## Part 1:一句話 prompt

`part1_naive/naive.py` 用最天真的方式生圖:

```python
PROMPT = "a cat"  # bare. no style, no lighting, no composition -> uncontrolled
```

```
GEMINI_API_KEY=xxx uv run python part1_naive/naive.py
```

會生出一張貓,但每次都不一樣 —— 姿勢、畫風、背景、光線全是模型替你決定的。要拿來做產品時,「每次都隨機」就是痛點。`naive.py` 自己的收尾就點明了這件事:

```
saved naive_cat.png  (run again -> a different cat, every time)
```

## Part 2:結構化 prompt

`demo_structured.py` 用 `build_prompt` 把每個決定命名出來:

```python
prompt = build_prompt(
    "a cat sitting by a window",
    style="ukiyo-e woodblock print",
    lighting="soft morning light",
    composition="centered, close-up",
    color="muted indigo and gold",
    negative="text, watermark, extra limbs",
)
```

組出來的真實 prompt 字串是:

```
a cat sitting by a window, style: ukiyo-e woodblock print, lighting: soft morning light, composition: centered, close-up, color palette: muted indigo and gold. Avoid: text, watermark, extra limbs
```

同樣的欄位永遠組出同樣這段字 —— 這就是可重現的來源。注意最後那段 `Avoid: ...`:這是 `negative` 欄位變來的,讓你能主動「說出要避免什麼」(文字、浮水印、多餘的肢體),這是一句話 prompt 做不到的。

```
GEMINI_API_KEY=xxx uv run python demo_structured.py
```

收尾的語意:

```
saved structured_cat.png  (same fields -> same kind of picture, every time)
```

## 結構化 prompt 的六個欄位

對應 `app/prompt.py` 的 `build_prompt`,把每個欄位當成一個你可以單獨調的旋鈕:

- **主體(subject)** — 必填,畫什麼。例:`a cat sitting by a window`。
- **style** — 畫風 / 媒材。例:`ukiyo-e woodblock print`、`flat vector`、`watercolor`。
- **lighting** — 光線。例:`soft morning light`、`dramatic rim light`。
- **composition** — 構圖 / 取景。例:`centered, close-up`、`wide shot, rule of thirds`。
- **color** — 配色。例:`muted indigo and gold`。
- **negative** — 要避免的東西,會變成 `Avoid: ...`。例:`text, watermark, extra limbs`。

寫得越具體,可控性越高、結果越穩定。要更接近「同一張」,就是把每個欄位寫得更精確;反過來,留白的欄位就是你交給模型發揮的空間。

## 動手練習

1. 只改 `style` 一個欄位(其他不動),跑兩種風格,感受「換一個旋鈕」的效果。
2. 把 `negative` 拿掉再加回來,看 `Avoid: ...` 對結果的影響。
3. 用同一組欄位跑兩次,確認描述字串完全一致(這就是可重現性)。`build_prompt` 是純函式,不需要 key 也能驗:`tests/test_prompt.py` 就斷言了「同樣輸入必給同樣 prompt」。
4. 想做整套(系列貼圖 / 一組角色),把欄位包進迴圈批次跑,見 `docs/06`。

## 延伸資源

把結構化 prompt 的想法做成現成工具:

- [PromptFill](https://github.com/yazelin/PromptFill) — 結構化提示詞工具,把「填欄位 → 組 prompt」做成可操作的介面。
- [prompts-vault](https://github.com/yazelin/prompts-vault) — Nano Banana(Gemini 影像)prompt 收集站,現成的高品質 prompt 可以照抄、改造。

## 真實案例:把生圖做成產品

當你能穩定、可控地生圖,下一步就是做成產品。這兩個是把同一套想法落地的真實專案:

- [line-sticker-studio](https://github.com/yazelin/line-sticker-studio) — 用 AI 生圖做成整套 LINE 貼圖的工作流。
- [catime](https://github.com/yazelin/catime) — 把生圖能力包進實際應用的範例。

想把這套帶進公司流程或做成課程,見 `docs/07`。
