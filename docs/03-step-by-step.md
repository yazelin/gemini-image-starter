# 用 AI 生圖入門:帶你走一遍

這份文件不是六條指路,而是帶你「實際做過」一遍:從零做出結構化 prompt builder、做出對齊真實 Gemini 的 gen client、再用本地假 server 把整條路徑測起來。最後親手擴充一個 prompt 欄位。所有輸出都是真的跑出來貼上的。

讀之前先記住一件事:**Part 2 的核心不是 API,而是 prompt 怎麼寫。** Part 1 一句 `"a cat"` 把所有決定交給模型;Part 2 把每個決定寫進結構化 prompt,拿回控制權。

> 開始前請先在 repo 根目錄跑過一次 `uv sync`(uv 安裝方式見 `01-quickstart.md`)。本文所有指令都用 `uv run python ...`,它會在 uv 建好的 `.venv` 裡執行;`uv sync` / `uv run` 在 Ubuntu 與 Windows 完全相同。**整份教學不需要 API key、不需要連網。**

## 步驟 1:先親眼看到「不可控」(Part 1)

Part 1 的 `part1_naive/naive.py` 只有一句關鍵:

```python
PROMPT = "a cat"  # bare. no style, no lighting, no composition -> uncontrolled
```

一句 `"a cat"` 丟給 Gemini,會生出一張貓 —— 但**每次都不一樣**:姿勢、畫風、背景、光線全是模型替你決定的。要拿來做產品(貼圖、頭像、角色)時,「每次都隨機」就是痛點。

(這一步真的執行需要 key,留到 `04-deployment.md`。這裡先記住痛點:一句話 = 不可控。)

## 步驟 2:做出結構化 prompt builder(純函式)

把控制權拿回來的方法,是把「每個會影響成品的決定」都寫成具名欄位。這就是 `app/prompt.py` 的 `build_prompt()`:

```python
def build_prompt(
    subject: str,
    *,
    style: str | None = None,
    lighting: str | None = None,
    composition: str | None = None,
    color: str | None = None,
    extra: str | None = None,
    negative: str | None = None,
) -> str:
    parts = [subject.strip()]
    if style:
        parts.append(f"style: {style.strip()}")
    if lighting:
        parts.append(f"lighting: {lighting.strip()}")
    if composition:
        parts.append(f"composition: {composition.strip()}")
    if color:
        parts.append(f"color palette: {color.strip()}")
    if extra:
        parts.append(extra.strip())
    prompt = ", ".join(parts)
    if negative:
        prompt += f". Avoid: {negative.strip()}"
    return prompt
```

重點:

- 它是**純函式** —— 沒有網路、沒有 key、沒有副作用。同樣的輸入永遠回同樣的字串。這就是「可重現」。
- 有填的欄位才出現,順序固定:主體 → style → lighting → composition → color palette → extra。
- `negative` 變成結尾的 `. Avoid: ...`,模型會把它當成「不要出現的東西」。

`demo_structured.py` 就是這樣用它的:

```python
prompt = build_prompt(
    "a cat sitting by a window",
    style="ukiyo-e woodblock print",
    lighting="soft morning light",
    composition="centered, close-up",
    color="muted indigo and gold",
    negative="text, watermark, extra limbs",
)
print("prompt:", prompt)
```

跑跑看(免 key,沒設 key 時只印 prompt):

```bash
uv run python demo_structured.py
```

真實輸出:

```
prompt: a cat sitting by a window, style: ukiyo-e woodblock print, lighting: soft morning light, composition: centered, close-up, color palette: muted indigo and gold. Avoid: text, watermark, extra limbs
```

成功的話你會看到:一條把每個決定都寫清楚的 prompt。對照 Part 1 的 `"a cat"`,差別一眼就懂 —— 風格、光線、構圖、配色、要避免的東西,全都被你寫進去了。

## 步驟 3:做出對齊真實 Gemini 的 gen client

光有 prompt 還不夠,要把它送進 Gemini。`app/gen.py` 對齊真實 Google Gemini 的生圖 API,並刻意拆成「純函式」和「真的打網路」兩部分。

先是兩個純函式 —— 它們是 client 的形狀,完全可測:

```python
def build_request_body(prompt: str) -> dict:
    return {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }

def extract_image(result: dict) -> bytes:
    candidates = result.get("candidates", [])
    if candidates:
        for part in candidates[0].get("content", {}).get("parts", []):
            data = part.get("inlineData", {}).get("data")
            if data:
                return base64.b64decode(data)
    raise ValueError("no image found in response")
```

`build_request_body` 把 prompt 包成 Gemini 要的 body:`contents[].parts[].text` 放 prompt,`generationConfig.responseModalities:["IMAGE"]` 告訴 Gemini「我要圖,不是文字」。`extract_image` 反過來,從回應裡找第一個 `inlineData.data`(base64),解碼成圖片 bytes;找不到就丟清楚的 `ValueError`。

接著是真的打網路的 `generate()`,把上面兩個純函式串起來:

```python
def generate(prompt, api_key, *, model=DEFAULT_MODEL, base_url=GEMINI_BASE, timeout=60.0) -> bytes:
    url = f"{base_url}/{model}:generateContent?key={api_key}"
    resp = httpx.post(url, json=build_request_body(prompt), timeout=timeout)
    resp.raise_for_status()
    return extract_image(resp.json())
```

注意 `base_url` 是**參數**,預設指向真實 Google 服務。下一步我們就靠它,把同一份 client 指向本地假 server 來測。

## 步驟 4:用假 server 把整條路徑測起來(免 key)

`tests/fake_gemini.py` 是一個用標準函式庫寫的迷你 HTTP server,對任何 POST 都回 Gemini 形狀的回應,`inlineData.data` 是一張固定的 1x1 PNG:

```python
class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)
        body = json.dumps(
            {"candidates": [{"content": {"parts": [
                {"inlineData": {"mimeType": "image/png", "data": PNG_B64}}]}}]}
        ).encode()
        self.send_response(200)
        ...

def start():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/v1beta/models"
```

`test_gen_fake.py` 把它接上真實 client 路徑 —— 關鍵就是把 `generate()` 的 `base_url` 指向這個假 server:

```python
server, base_url = start()
try:
    img = generate("a cat, style: ukiyo-e", api_key="fake-key", base_url=base_url)
    assert img == base64.b64decode(PNG_B64), "decoded image bytes mismatch"

    out = pathlib.Path(tempfile.gettempdir()) / "_gen_fake_test.png"
    save_image(img, str(out))
    assert out.read_bytes() == img, "saved file bytes mismatch"
    out.unlink()
    print("OK: gen against fake Gemini server passed")
finally:
    server.shutdown()
```

這就走完了 build body → POST → 解析 `inlineData` → base64 解碼 → 存檔 → 讀回比對的完整流程,**而且用的是假 key、本地 server,完全不碰外網。** 這就是為什麼測試能涵蓋真實路徑卻不需要 GEMINI_API_KEY。

跑全部三個測試:

```bash
uv run python client_smoke_test.py
```

真實輸出:

```
== tests/test_prompt.py ==
OK: prompt builder test passed

== tests/test_request.py ==
OK: request/response shaping test passed

== tests/test_gen_fake.py ==
OK: gen against fake Gemini server passed

OK: all checks passed
```

成功的話你會看到:三段 `OK:`,以 `OK: all checks passed` 收尾。看到這行,代表 prompt 設計、API 形狀、整條生圖流程都通了。

## 動手練習:加一個 prompt 欄位

換你擴充 `build_prompt`。建議加一個 `mood`(氣氛)欄位,例如 `mood="cozy and quiet"` 會在 prompt 裡多一段 `mood: cozy and quiet`。

提示:

1. 在 `build_prompt` 的參數加 `mood: str | None = None`(放在 `*` 之後,跟其他具名欄位並列)。
2. 在組 `parts` 的地方仿照 `style` 加一段:

   ```python
   if mood:
       parts.append(f"mood: {mood.strip()}")
   ```

3. 在 `demo_structured.py` 的 `build_prompt(...)` 呼叫裡傳 `mood="cozy and quiet"`,再跑:

```bash
uv run python demo_structured.py
```

預期 prompt 裡會多出 `mood: cozy and quiet`。如果沒出現,先檢查:參數加了但組 `parts` 那段忘了加(或欄位名拼錯);如果報 `unexpected keyword argument 'mood'`,代表 `demo_structured.py` 傳了參數但 `build_prompt` 還沒加這個參數。

加完不用改任何測試也能跑通 —— 因為 `build_prompt` 是純函式,新欄位選填、不影響舊行為。想驗證可重現性,把同一組輸入呼叫兩次,結果字串會完全相同。
