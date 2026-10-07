"""
AI Text Translation Tool
Author: Naman Mujawdiya
Translation: MyMemory Translation API
UI: Gradio
"""

import gradio as gr
import urllib.request
import urllib.parse
import json


# ---------------------------------------------------------------
# 1. Supported Languages
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
# 2. Translation Function
# ---------------------------------------------------------------

def translate_text(text, source_lang, target_lang):

    if not text or not text.strip():
        return "Please enter some text."

    if source_lang == target_lang:
        return text.strip()

    source_code = LANGUAGES[source_lang]
    target_code = LANGUAGES[target_lang]

    try:
        # MyMemory API
        url = "https://api.mymemory.translated.net/get?"

        params = {
            "q": text.strip(),
            "langpair": f"{source_code}|{target_code}"
        }

        full_url = url + urllib.parse.urlencode(params)

        request = urllib.request.Request(
            full_url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("responseStatus") == 200:

            translated = data.get("responseData", {}).get(
                "translatedText", ""
            )

            if translated:
                return translated

        return "Translation failed. Please try again."

    except Exception as e:
        return f"Translation Error: {str(e)}"


# ---------------------------------------------------------------
# 3. Swap Function
# ---------------------------------------------------------------

def swap_languages(source, target, input_text, output_text):

    return target, source, output_text, input_text


# ---------------------------------------------------------------
# 4. Gradio UI
# ---------------------------------------------------------------

with gr.Blocks(title="AI Text Translation Tool") as demo:

    gr.Markdown(
        """
        # 🌐 AI Text Translation Tool

        Translate text between multiple languages using a lightweight
        translation approach.
        """
    )

    # Language selection
    with gr.Row():

        source_dropdown = gr.Dropdown(
            choices=list(LANGUAGES.keys()),
            value="English",
            label="From (Source)"
        )

        swap_button = gr.Button("⇄ Swap", scale=0)

        target_dropdown = gr.Dropdown(
            choices=list(LANGUAGES.keys()),
            value="Hindi",
            label="To (Target)"
        )

    # Text boxes
    with gr.Row():

        input_text = gr.Textbox(
            lines=7,
            label="Enter Text",
            placeholder="Type or paste your text here..."
        )

        output_text = gr.Textbox(
            lines=7,
            label="Translation",
            interactive=False
        )

    # Translate button
    translate_button = gr.Button(
        "🌐 Translate",
        variant="primary"
    )

    # Translation event
    translate_button.click(
        fn=translate_text,
        inputs=[
            input_text,
            source_dropdown,
            target_dropdown
        ],
        outputs=output_text
    )

    # Swap event
    swap_button.click(
        fn=swap_languages,
        inputs=[
            source_dropdown,
            target_dropdown,
            input_text,
            output_text
        ],
        outputs=[
            source_dropdown,
            target_dropdown,
            input_text,
            output_text
        ]
    )

    # Examples
    gr.Examples(
        examples=[
            [
                "Hello, how are you?",
                "English",
                "Hindi"
            ],
            [
                "Technology is changing the world.",
                "English",
                "Spanish"
            ],
            [
                "I love learning new technologies.",
                "English",
                "French"
            ]
        ],
        inputs=[
            input_text,
            source_dropdown,
            target_dropdown
        ]
    )


# ---------------------------------------------------------------
# 5. Start Application
# ---------------------------------------------------------------

if _name_ == "_main_":
    demo.launch(
        server_name="0.0.0.0",
        server_port=10000
    )
