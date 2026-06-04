# Part 1 · 一句話 prompt(baseline)

`naive.py` 用最天真的方式生圖:一句 `"a cat"` 丟給 Gemini。

```
GEMINI_API_KEY=xxx uv run python part1_naive/naive.py
```

會生出一張貓 —— 但**每次都不一樣**:姿勢、畫風、背景、光線全是模型替你決定的。要拿來做產品(貼圖、頭像、角色)時,這種「每次都隨機」就是痛點。

→ Part 2(`app/prompt.py`)用**結構化 prompt**(主體 / 風格 / 光線 / 構圖 / 配色 / 負面詞)把這些決定權拿回來:同樣的輸入 → 同樣的描述 → 可控、可重現。這就是「繪圖魔法師」的第一個魔法:**prompt 設計**。

對照課:`docs/08-prompt-engineering.md`。
