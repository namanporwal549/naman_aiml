"""
AI Text Translation Tool
Author: Naman Mujawdiya
Lightweight version for Render deployment
UI: Gradio
"""

import os
import gradio as gr
from deep_translator import GoogleTranslator


# ---------------------------------------------------------------
# Supported languages
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
# ---------------------------------------------------------------
# Translation function
# ---------------------------------------------------------------
def translate(text, source_lang, target_lang):

    if not text or not text.strip():
        return "Please enter some text."

    if source_lang == target_lang:
        return text

    try:
        translator = GoogleTranslator(
            source=LANGUAGES[source_lang],
            target=LANGUAGES[target_lang]
        )

        result = translator.translate(text.strip())

        return result

    except Exception as e:
        return f"Translation Error: {e}"


# ---------------------------------------------------------------
# Swap function
# ---------------------------------------------------------------
def swap(src, tgt, input_text, output_text):
    return tgt, src, output_text, input_text


# ---------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------
with gr.Blocks(title="AI Text Translator") as demo:

    gr.Markdown(
        "# 🌐 AI Text Translation Tool\n"
        "Translate text between multiple languages."
    )

    with gr.Row():

        src_dd = gr.Dropdown(
            choices=list(LANGUAGES.keys()),
            value="English",
            label="From (Source)"
        )

        swap_btn = gr.Button("⇄ Swap", scale=0)

        tgt_dd = gr.Dropdown(
            choices=list(LANGUAGES.keys()),
            value="Hindi",
            label="To (Target)"
        )

    with gr.Row():

        inp = gr.Textbox(
            lines=6,
            label="Enter text",
            placeholder="Type your text here..."
        )

        out = gr.Textbox(
            lines=6,
            label="Translation",
            interactive=False
        )

    translate_btn = gr.Button(
        "Translate",
        variant="primary"
    )

    translate_btn.click(
        translate,
        inputs=[inp, src_dd, tgt_dd],
        outputs=out
    )

    swap_btn.click(
        swap,
        inputs=[src_dd, tgt_dd, inp, out],
        outputs=[src_dd, tgt_dd, inp, out]
    )

    gr.Examples(
        examples=[
            ["Hello, how are you?", "English", "Hindi"],
            ["Technology is changing the world.", "English", "Spanish"],
            ["Mujhe ye project bahut pasand aaya.", "Hindi", "French"],
        ],
        inputs=[inp, src_dd, tgt_dd]
    )


# ---------------------------------------------------------------
# Start server
# ---------------------------------------------------------------
if _name_ == "_main_":

    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 10000))
    )
