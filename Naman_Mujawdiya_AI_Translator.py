"""
AI Text Translation Tool  (lightweight version)
Author: Naman Mujawdiya

- Koi model download nahi (sirf `requests` + `gradio`) -> deploy karna easy
- 2 translation engines: Google Translate (primary) -> MyMemory (fallback)
- 429 / network error aaye to automatic retry + fallback
- Same text dobara translate karne par cache se instant result
"""

import re
import time
from functools import lru_cache

import gradio as gr
import requests

# ---------------------------------------------------------------
# 1. Languages (display name -> ISO code)
# ---------------------------------------------------------------
LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Tamil": "ta",
    "Telugu": "te",
    "Urdu": "ur",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese (Simplified)": "zh-CN",
    "Arabic": "ar",
}
AUTO = "Auto-detect"
SOURCE_CHOICES = [AUTO] + list(LANGUAGES)
TARGET_CHOICES = list(LANGUAGES)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TranslatorDemo/1.0)"}
CHUNK_SIZE = 300  # chhote chunks -> kam errors, MyMemory ki 500 char limit ke andar


# ---------------------------------------------------------------
# 2. Translation engines
# ---------------------------------------------------------------
def google_translate(text, src, tgt):
    r = requests.get(
        "https://translate.googleapis.com/translate_a/single",
        params={"client": "gtx", "sl": src, "tl": tgt, "dt": "t", "q": text},
        headers=HEADERS,
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    return "".join(part[0] for part in data[0] if part and part[0])


def mymemory_translate(text, src, tgt):
    pair = f"{'Autodetect' if src == 'auto' else src}|{tgt}"
    r = requests.get(
        "https://api.mymemory.translated.net/get",
        params={"q": text, "langpair": pair},
        headers=HEADERS,
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    out = data["responseData"]["translatedText"]
    if str(data.get("responseStatus")) != "200" or "MYMEMORY WARNING" in out:
        raise RuntimeError("MyMemory limit/err")
    return out


ENGINES = [("Google Translate", google_translate), ("MyMemory", mymemory_translate)]


def with_retry(fn, text, src, tgt, attempts=3):
    """429 ya temporary error par 1s, 2s wait karke dobara try karta hai."""
    last_err = None
    for i in range(attempts):
        try:
            return fn(text, src, tgt)
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(2 ** i * 0.8)
    raise last_err


@lru_cache(maxsize=512)
def translate_chunk(text, src, tgt):
    """Pehle Google, fail ho to MyMemory. Returns (translation, engine_name)."""
    errors = []
    for name, fn in ENGINES:
        try:
            return with_retry(fn, text, src, tgt), name
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name}: {e}")
    raise RuntimeError(" | ".join(errors))


def split_text(text, size=CHUNK_SIZE):
    """Lambe text ko sentences ke hisaab se chhote chunks me todta hai."""
    sentences = re.split(r"(?<=[.!?।])\s+", text.strip())
    chunks, cur = [], ""
    for s in sentences:
        while len(s) > size:  # bahut lambi sentence
            chunks.append(s[:size])
            s = s[size:]
        if len(cur) + len(s) + 1 <= size:
            cur = f"{cur} {s}".strip()
        else:
            if cur:
                chunks.append(cur)
            cur = s
    if cur:
        chunks.append(cur)
    return chunks


# ---------------------------------------------------------------
# 3. Main function
# ---------------------------------------------------------------
def translate(text, source_lang, target_lang):
    if not text or not text.strip():
        return "Please enter some text.", ""
    src = "auto" if source_lang == AUTO else LANGUAGES[source_lang]
    tgt = LANGUAGES[target_lang]
    if src == tgt:
        return text, "Same language - no translation needed"
    try:
        parts, engines = [], set()
        for chunk in split_text(text):
            result, engine = translate_chunk(chunk, src, tgt)
            parts.append(result)
            engines.add(engine)
        return " ".join(parts), "Engine: " + ", ".join(sorted(engines))
    except Exception:  # noqa: BLE001
        return (
            "Translation service is busy right now. Please try again in a few seconds.",
            "All engines temporarily unavailable",
        )


def swap(src, tgt, inp, out):
    if src == AUTO:  # auto-detect ko target nahi bana sakte
        return src, tgt, inp, out
    return tgt, src, out, inp


# ---------------------------------------------------------------
# 4. UI
# ---------------------------------------------------------------
with gr.Blocks(title="AI Text Translator") as demo:
    gr.Markdown(
        "# 🌐 AI Text Translation Tool\n"
        "Translate text between 18 languages. Lightweight, fast and with automatic fallback."
    )
    with gr.Row():
        src_dd = gr.Dropdown(SOURCE_CHOICES, value="English", label="From (Source)")
        swap_btn = gr.Button("⇄ Swap", scale=0)
        tgt_dd = gr.Dropdown(TARGET_CHOICES, value="Hindi", label="To (Target)")
    with gr.Row():
        inp = gr.Textbox(lines=7, label="Enter text", placeholder="Type or paste text here...")
        out = gr.Textbox(lines=7, label="Translation", interactive=False)
    status = gr.Markdown()
    btn = gr.Button("🌐 Translate", variant="primary")

    btn.click(translate, [inp, src_dd, tgt_dd], [out, status])
    swap_btn.click(swap, [src_dd, tgt_dd, inp, out], [src_dd, tgt_dd, inp, out])

    gr.Examples(
        [
            ["Hello, how are you?", "English", "Hindi"],
            ["Technology is changing the world.", "English", "Spanish"],
            ["I love learning new technologies.", "English", "French"],
        ],
        inputs=[inp, src_dd, tgt_dd],
    )

if __name__ == "__main__":
    demo.launch()
