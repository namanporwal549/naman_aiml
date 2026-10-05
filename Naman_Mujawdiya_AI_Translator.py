"""
AI Text Translation Tool
Author: Naman Mujawdiya
Model : facebook/nllb-200-distilled-600M (open-source, multi-language, no API key needed)
UI    : Gradio

Google Colab me pehle ye cell chalao:
    !pip install -q transformers sentencepiece gradio torch
Phir is poori file ko ek cell me paste karke run karo.
"""

import gradio as gr
import torch
from transformers import pipeline

# ---------------------------------------------------------------
# 1. Supported languages  (display name -> NLLB language code)
# ---------------------------------------------------------------
LANGUAGES = {
    "English": "eng_Latn",
    "Hindi": "hin_Deva",
    "Marathi": "mar_Deva",
    "Bengali": "ben_Beng",
    "Gujarati": "guj_Gujr",
    "Tamil": "tam_Taml",
    "Telugu": "tel_Telu",
    "Urdu": "urd_Arab",
    "French": "fra_Latn",
    "German": "deu_Latn",
    "Spanish": "spa_Latn",
    "Italian": "ita_Latn",
    "Portuguese": "por_Latn",
    "Russian": "rus_Cyrl",
    "Japanese": "jpn_Jpan",
    "Korean": "kor_Hang",
    "Chinese (Simplified)": "zho_Hans",
    "Arabic": "arb_Arab",
}

MODEL_NAME = "facebook/nllb-200-distilled-600M"

# ---------------------------------------------------------------
# 2. Load model once (GPU use hoga agar available ho)
# ---------------------------------------------------------------
device = 0 if torch.cuda.is_available() else -1
print("Loading model... (pehli baar thoda time lagega)")
_cache = {}


def get_translator(src_code, tgt_code):
    """Same model reuse hota hai, sirf language codes change hote hain."""
    key = (src_code, tgt_code)
    if key not in _cache:
        _cache[key] = pipeline(
            "translation",
            model=MODEL_NAME,
            src_lang=src_code,
            tgt_lang=tgt_code,
            max_length=400,
            device=device,
        )
    return _cache[key]


# ---------------------------------------------------------------
# 3. Translation function
# ---------------------------------------------------------------
def translate(text, source_lang, target_lang):
    if not text or not text.strip():
        return "Please enter some text."
    if source_lang == target_lang:
        return text  # same language, kuch karna nahi
    try:
        translator = get_translator(LANGUAGES[source_lang], LANGUAGES[target_lang])
        result = translator(text.strip())
        return result[0]["translation_text"]
    except Exception as e:
        return f"Error: {e}"


def swap(src, tgt, input_text, output_text):
    """Source aur target language (aur text) swap karne ke liye."""
    return tgt, src, output_text, input_text


# ---------------------------------------------------------------
# 4. Gradio UI
# ---------------------------------------------------------------
with gr.Blocks(title="AI Text Translator") as demo:
    gr.Markdown("# 🌐 AI Text Translation Tool\nPowered by Meta NLLB-200 (open-source)")

    with gr.Row():
        src_dd = gr.Dropdown(list(LANGUAGES), value="English", label="From (Source)")
        swap_btn = gr.Button("⇄ Swap", scale=0)
        tgt_dd = gr.Dropdown(list(LANGUAGES), value="Hindi", label="To (Target)")

    with gr.Row():
        inp = gr.Textbox(lines=6, label="Enter text", placeholder="Type here...")
        out = gr.Textbox(lines=6, label="Translation", interactive=False)

    translate_btn = gr.Button("Translate", variant="primary")

    translate_btn.click(translate, [inp, src_dd, tgt_dd], out)
    swap_btn.click(swap, [src_dd, tgt_dd, inp, out], [src_dd, tgt_dd, inp, out])

    gr.Examples(
        examples=[
            ["Hello, how are you?", "English", "Hindi"],
            ["Mujhe ye project bahut pasand aaya.", "English", "French"],
            ["Technology is changing the world.", "English", "Spanish"],
        ],
        inputs=[inp, src_dd, tgt_dd],
    )

if __name__ == "__main__":
    demo.launch(share=True)  # share=True se Colab me public link milta hai
