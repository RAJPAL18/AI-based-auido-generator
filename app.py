# app.py

import os
import base64
from pathlib import Path
from typing import List

import streamlit as st
from dotenv import load_dotenv

from utils.extract_text import extract_text_any
from utils.chapters import split_into_chapters
from utils.nlp import (
    detect_language,
    translate_and_rephrase,
    SUPPORTED_LANGUAGES,
)
from utils.tts import text_to_speech_mp3

# Load environment variables (for local GEMINI_API_KEY)
load_dotenv()

# Ensure audio output directory exists
Path("outputs/audio").mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="Multilingual AI Audiobook Generator",
    page_icon="🎧",
    layout="wide",
)


# --------------------------------------------------------------------
# BACKGROUND IMAGE
# --------------------------------------------------------------------
def set_background(image_path: str):
    """Set a full-page background image with a dark overlay and readable text."""
    if not os.path.exists(image_path):
        return

    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <style>
        /* Background image with dark overlay */
        .stApp {{
            background: 
                linear-gradient(rgba(0, 0, 0, 0.70), rgba(0, 0, 0, 0.70)),
                url("data:image/png;base64,{encoded}") center/cover no-repeat fixed;
        }}

        /* Main content container slightly dark so text is clear */
        .block-container {{
            background-color: rgba(0, 0, 0, 0.55);
            border-radius: 12px;
            padding: 1.5rem 2rem;
        }}

        /* Sidebar background */
        [data-testid="stSidebar"] {{
            background-color: rgba(0, 0, 0, 0.80);
        }}

        /* Make all main text light */
        h1, h2, h3, h4, h5, h6,
        p, li, span, label, .stMarkdown, .stText, .stCaption, .stCheckbox, .stRadio {{
            color: #f9fafb !important;
        }}

        /* Tabs styling for readability */
        .stTabs [role="tab"] {{
            background-color: rgba(15, 23, 42, 0.85);
            color: #e5e7eb !important;
            border-radius: 12px 12px 0 0;
        }}
        .stTabs [role="tab"][aria-selected="true"] {{
            background-color: rgba(30, 64, 175, 0.9);
            color: #ffffff !important;
        }}

        /* Text areas & inputs background */
        textarea, input, .stTextInput > div > div > input {{
            background-color: rgba(15, 23, 42, 0.9) !important;
            color: #e5e7eb !important;
        }}

        /* Buttons */
        .stButton > button {{
            background-color: #f97316 !important;
            color: white !important;
            border-radius: 999px;
            border: none;
        }}
        .stButton > button:hover {{
            background-color: #ea580c !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )



# --------------------------------------------------------------------
# MAIN ENTRY
# --------------------------------------------------------------------
def main():
    # Set background once
    set_background("assets/banner.png")

    # ====== PAGE TITLE ======
    st.title("🎧 Multilingual AI Audiobook Generator")

    # ====== TABS ======
    tab_overview, tab_generate, tab_about = st.tabs(
        ["📘 Overview", "⚙️ Process / Generate", "ℹ️ About App"]
    )

    with tab_overview:
        render_overview_tab()

    with tab_generate:
        render_generate_tab()

    with tab_about:
        render_about_tab()

    # ====== FOOTER ======
    st.markdown(
        "<hr style='margin-top:2rem;margin-bottom:0.5rem;'>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;font-size:0.9rem;'>"
        "Made by <b>Rajpal Rajput</b>"
        "</p>",
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------
# OVERVIEW TAB
# --------------------------------------------------------------------
def render_overview_tab():
    st.subheader("📘 What this app does")

    st.markdown(
        """
        This app converts your **PDF / DOCX / TXT** documents into multilingual audiobooks.

        **Key capabilities:**
        - 🔍 Detects the **original language** of the document automatically  
        - 🌍 Translates and rewrites text into an **audiobook-style narration**  
        - 🎙 Generates audio in:
          - the **original language**, and/or  
          - a **selected target language**  
        - 📥 Lets you **download chapter-wise MP3 files**
        """
    )

    st.markdown("### 🔄 Processing Pipeline")
    st.markdown(
        """
        1️⃣ **Upload document** (PDF / DOCX / TXT)  
        2️⃣ **Extract text** from pages  
        3️⃣ **Split into chapters** based on headings / length  
        4️⃣ **Detect original language** using AI (Gemini)  
        5️⃣ **Translate + rephrase** into the target language in audiobook style  
        6️⃣ **Generate audio** (original & translated) using Text-to-Speech  
        7️⃣ **Listen or download** MP3 per chapter  
        """
    )

    st.markdown("### 🌍 Supported Languages")
    st.write(
        "- English\n"
        "- Hindi\n"
        "- Marathi\n"
        "- Tamil\n"
        "- Telugu\n"
        "- Bengali\n"
        "- Gujarati"
    )

    st.info(
        "Tip: Start with a small TXT or short PDF first to test the flow, "
        "then try larger documents."
    )


# --------------------------------------------------------------------
# GENERATE TAB (MAIN FUNCTIONALITY)
# --------------------------------------------------------------------
def render_generate_tab():
    st.subheader("⚙️ Upload & Generate Audiobooks")

    # ====== SETTINGS (TOP AREA) ======
    with st.expander("🎛 Global Settings", expanded=True):
        cols = st.columns(3)
        with cols[0]:
            target_language = st.selectbox(
                "Output language (translated audiobook)",
                options=list(SUPPORTED_LANGUAGES.keys()),
                index=0,
            )
        with cols[1]:
            generate_original = st.checkbox(
                "🎵 Original-language audio", value=True
            )
            generate_translated = st.checkbox(
                f"🌍 Translated audiobook ({target_language})",
                value=True,
            )
        with cols[2]:
            accent = st.selectbox(
                "Voice accent (approx.)",
                options=["com", "co.in", "co.uk", "com.au"],
                index=1,
                help="com = US, co.in = Indian, co.uk = British, com.au = Australian.",
            )
            slow_voice = st.checkbox("🐢 Slower speech", value=False)

    # ====== FILE UPLOAD SECTION ======
    st.markdown("### 📂 Upload your documents")
    uploaded_files = st.file_uploader(
        "Upload one or more documents",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, TXT",
    )

    col_btn, _ = st.columns([1, 3])
    with col_btn:
        generate_clicked = st.button(
            "🚀 Start Processing", use_container_width=True
        )

    if generate_clicked:
        if not (generate_original or generate_translated):
            st.warning("Please select at least one audio type to generate.")
        elif not uploaded_files:
            st.warning("Please upload at least one document.")
        else:
            process_files(
                uploaded_files=uploaded_files,
                target_language=target_language,
                accent=accent,
                slow_voice=slow_voice,
                generate_original=generate_original,
                generate_translated=generate_translated,
            )


# --------------------------------------------------------------------
# ABOUT TAB
# --------------------------------------------------------------------
def render_about_tab():
    st.subheader("ℹ️ About This Application")

    st.markdown(
        """
        This project is a **Multilingual AI-based Audiobook Generator** built using:

        - 🐍 **Python**
        - 🧠 **Google Gemini** for language detection, translation & rephrasing
        - 🗣 **gTTS** for generating MP3 audio
        - 🧾 **PyPDF2 / python-docx** for text extraction
        - 🖥 **Streamlit** for the interactive web interface

        **Core Idea:**  
        Make it easy to convert documents into audio, in multiple languages, for:
        - Students and readers  
        - Visually impaired users  
        - Multilingual learning  
        - Content creators and educators  
        """
    )

    st.markdown("### 👨‍💻 Developer")
    st.markdown(
        """
        **Name:** Rajpal Rajput  
        **Role:** B.Tech AI & Data Science student, creator of this project  
        """
    )

    st.markdown("### ✅ Features Summary")
    st.write(
        "- Automatic language detection\n"
        "- Translation + rephrasing into audiobook style\n"
        "- Dual audio: original & translated\n"
        "- Chapter-wise processing & downloads\n"
    )

    st.markdown("### 📬 Future Enhancements")
    st.write(
        "- More natural neural TTS voices (e.g., OpenAI TTS)\n"
        "- One-click full-book MP3 export\n"
        "- Add background music & sound design\n"
        "- Support for EPUB and web article URLs\n"
    )


# --------------------------------------------------------------------
# CORE PROCESSING LOGIC
# --------------------------------------------------------------------
def process_files(
    uploaded_files: List,
    target_language: str,
    accent: str,
    slow_voice: bool,
    generate_original: bool,
    generate_translated: bool,
):
    target_tts_code = SUPPORTED_LANGUAGES.get(target_language, "en")

    for file in uploaded_files:
        file_name = file.name
        base_name = Path(file_name).stem

        st.markdown("---")
        st.header(f"📄 {file_name}")

        try:
            # 1. Extract text
            raw_text = extract_text_any(file_name, file)
            if not raw_text.strip():
                st.error("No text could be extracted from this file.")
                continue

            with st.expander("📝 Extracted Text Preview (partial)", expanded=False):
                st.text_area(
                    "Raw text preview",
                    raw_text[:3000],
                    height=200,
                    disabled=True,
                )

            # 2. Split into chapters
            chapters = split_into_chapters(raw_text)
            if not chapters:
                st.error("No chapters/content found after splitting.")
                continue

            st.success(f"✅ Found {len(chapters)} chapter(s).")

            # 3. Process each chapter
            for ch_idx, ch_text in enumerate(chapters, start=1):
                st.markdown(f"### 🎧 Chapter {ch_idx}")

                # 3a. Detect original language
                with st.spinner(f"Detecting language for Chapter {ch_idx}..."):
                    orig_lang_name, orig_tts_code = detect_language(ch_text)

                st.caption(f"Detected original language: **{orig_lang_name}**")

                # Two-column layout: text on left, audio on right
                text_col, audio_col = st.columns([2, 1])

                # ----- LEFT: TEXT -----
                with text_col:
                    st.markdown("#### 📌 Actual Content (Original)")
                    st.text_area(
                        f"Actual Text - Chapter {ch_idx}",
                        ch_text[:2000],
                        height=220,
                        disabled=True,
                    )

                    with st.spinner(
                        f"Translating & rephrasing Chapter {ch_idx} into {target_language}..."
                    ):
                        translated_text = translate_and_rephrase(ch_text, target_language)

                    st.markdown(
                        f"#### ✨ Translated & Rephrased Content ({target_language})"
                    )
                    st.text_area(
                        f"Rephrased Text - Chapter {ch_idx}",
                        translated_text[:2000],
                        height=220,
                        disabled=True,
                    )

                # ----- AUDIO GENERATION -----
                ch_base_name = f"{base_name}_chapter_{ch_idx}"
                orig_path = orig_bytes = None
                trans_path = trans_bytes = None

                if generate_original or generate_translated:
                    with st.spinner(
                        f"🎙 Generating selected audio for Chapter {ch_idx}..."
                    ):
                        # Original audio (detected language)
                        if generate_original:
                            orig_path, orig_bytes = text_to_speech_mp3(
                                ch_text,
                                output_dir="outputs/audio",
                                base_name=f"{ch_base_name}_original",
                                lang=orig_tts_code,
                                slow=slow_voice,
                                tld=accent,
                            )

                        # Translated & rephrased audio (target language)
                        if generate_translated:
                            trans_path, trans_bytes = text_to_speech_mp3(
                                translated_text,
                                output_dir="outputs/audio",
                                base_name=f"{ch_base_name}_translated_{target_language}",
                                lang=target_tts_code,
                                slow=slow_voice,
                                tld=accent,
                            )

                # ----- RIGHT: AUDIO PLAYERS -----
                with audio_col:
                    if generate_original and orig_bytes:
                        st.markdown("##### 🔊 Original Audio")
                        st.audio(orig_bytes, format="audio/mp3")
                        st.download_button(
                            label=f"Download Original – Ch {ch_idx}",
                            data=orig_bytes,
                            file_name=os.path.basename(orig_path),
                            mime="audio/mpeg",
                            key=f"download_orig_{ch_base_name}",
                        )

                    if generate_translated and trans_bytes:
                        st.markdown(
                            f"##### 🌍 Translated Audio ({target_language})"
                        )
                        st.audio(trans_bytes, format="audio/mp3")
                        st.download_button(
                            label=f"Download Translated – Ch {ch_idx}",
                            data=trans_bytes,
                            file_name=os.path.basename(trans_path),
                            mime="audio/mpeg",
                            key=f"download_trans_{ch_base_name}",
                        )

        except Exception as e:
            st.error(f"Error processing {file_name}: {e}")


if __name__ == "__main__":
    main()
