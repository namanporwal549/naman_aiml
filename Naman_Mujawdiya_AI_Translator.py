"""
AI Text Translation Tool
Author: Naman Mujawdiya
Model : facebook/nllb-200-distilled-600M (open-source, multi-language, no API key needed)
UI    : Gradio

Google Colab me pehle ye cell chalao:
    !pip install -q transformers sentencepiece gradio torch
Phir is poori file ko ek cell me paste karke run karo.
"""
import os
import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

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
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Loading model... (pehli baar thoda time lagega)")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)
model.eval()


def run_translation(text, src_code, tgt_code):
    """Model ek hi hai; source/target language codes se direction decide hoti hai."""
    tokenizer.src_lang = src_code
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=400).to(device)
    with torch.no_grad():
        generated = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_code),
            max_new_tokens=400,
            num_beams=4,
        )
    return tokenizer.batch_decode(generated, skip_special_tokens=True)[0]


# ---------------------------------------------------------------
# 3. Translation function
# ---------------------------------------------------------------
def translate(text, source_lang, target_lang):
    if not text or not text.strip():
        return "Please enter some text."
    if source_lang == target_lang:
        return text  # same language, kuch karna nahi
    try:
        return run_translation(text.strip(), LANGUAGES[source_lang], LANGUAGES[target_lang])
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
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 10000))
    )

