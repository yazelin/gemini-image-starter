# 繪圖魔法師入門:改成你的使用場景

跑通範例之後,這套東西怎麼長成你自己的工具?核心只有兩個檔:`app/prompt.py`(設計 prompt)和 `app/gen.py`(呼叫 Gemini)。下面幾個方向由淺到深。

## 1. 加 prompt 欄位

`app/prompt.py` 的 `build_prompt` 就是把命名欄位接成一段文字。現有欄位是主體 / style / lighting / composition / color / extra / negative。要加新維度(例如鏡頭、材質、年代風格),照同一個 pattern 加一個 keyword-only 參數,再 append 一段 `f"..."`:

```python
def build_prompt(subject, *, style=None, lighting=None, composition=None,
                 color=None, lens=None, extra=None, negative=None):
    parts = [subject.strip()]
    if style:
        parts.append(f"style: {style.strip()}")
    # ... 既有欄位 ...
    if lens:
        parts.append(f"lens: {lens.strip()}")   # 新欄位,同一套寫法
    prompt = ", ".join(parts)
    if negative:
        prompt += f". Avoid: {negative.strip()}"
    return prompt
```

這個函式是純函式(不碰網路、不需 key),所以加完欄位後在 `tests/test_prompt.py` 補一條斷言就能確定性驗證 —— 不花任何 API 額度。

## 2. 換 model

`app/gen.py` 已經把 model 抽成參數:

```python
DEFAULT_MODEL = "gemini-2.5-flash-image"  # fallback: gemini-2.0-flash-exp-image-generation
```

要換成別的 Gemini 影像模型,呼叫時傳 `model=` 即可,不用動 client:

```python
img = generate(prompt, key, model="gemini-2.0-flash-exp-image-generation")
```

`generate()` 會自己組 `{base_url}/{model}:generateContent?key=`,所以換 model 只是換字串。

## 3. 加 input image 做圖生圖(image-to-image)

目前 `build_request_body` 只塞一個 text part。Gemini 的 `contents[].parts[]` 可以同時帶 text 和 inline 圖片,要做「給一張參考圖 + 一段指令 → 改圖」時,在 parts 裡多加一個 `inlineData`:

```python
def build_edit_body(prompt: str, image_bytes: bytes, mime: str = "image/png") -> dict:
    b64 = base64.b64encode(image_bytes).decode()
    return {
        "contents": [{"parts": [
            {"inlineData": {"mimeType": mime, "data": b64}},
            {"text": prompt},
        ]}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }
```

回應形狀不變(一樣是 `candidates[0].content.parts[].inlineData.data`),所以 `extract_image` 不用改、可以直接重用。

## 4. 批次風格

把 `build_prompt` + `generate` 包成迴圈,就能用「同一個主體跑多種風格」或「同一種風格跑多個主體」。這正是把生圖變產品的常見第一步(整套貼圖、一系列角色頭像):

```python
styles = ["ukiyo-e woodblock print", "flat vector", "watercolor"]
for s in styles:
    p = build_prompt("a cat sitting by a window", style=s,
                     negative="text, watermark, extra limbs")
    img = generate(p, key)
    save_image(img, f"cat_{s.split()[0]}.png")
```

批次時記得免費額度有限流(見 `docs/05` 坑 5),迴圈裡加節流與重試,別一次燒光額度。

## 改造原則

- 一次只改一個層次:先改 prompt 欄位,再換 model,再加 input image,再做批次。
- 純邏輯先用無 key 測試鎖住:`build_prompt` / `build_request_body` / `extract_image` 都是純函式,改完先補 `tests/` 斷言,確定性驗證、零成本。
- 接真 API 前,先讓 `client_smoke_test.py` 全綠,確認你沒改壞 build→POST→解析→存檔這條路徑。
- 先做 PoC,再決定要不要產品化。把生圖做成正式產品的真實案例見 `docs/07`。

## 適合拿來做課程 / 工作坊的題目

- 從零跑起這個 starter(一句話 prompt → 結構化 prompt)。
- 把結構化 prompt 改成自己的真實場景(品牌貼圖、商品圖、角色設計)。
- 加 input image 做圖生圖,或做批次風格。
- 現場 debug 學員遇到的問題(拿不到圖、結果不可控、限流)。
