# app.py

from pathlib import Path
from typing import List
import os

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

# Load .env (for GEMINI_API_KEY)
load_dotenv()

# Ensure audio output dir exists
Path("outputs/audio").mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="Multilingual AI Audiobook Generator",
    page_icon="🎧",
    layout="centered",
)


def main():
    st.title("🎧 Multilingual AI Audiobook Generator")
    st.write(
        "Upload **PDF**, **DOCX**, or **TXT** files.\n\n"
        "- The app will detect the original language.\n"
        "- (Optional) Generate audio in the original language.\n"
        "- Translate + rephrase into your chosen language.\n"
        "- (Optional) Generate audiobook-style audio in the target language."
    )

    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    # Target language for translated audiobook
    target_language = st.selectbox(
        "Select output language for translated audiobook",
        options=list(SUPPORTED_LANGUAGES.keys()),
        index=0,
    )

    # Let user choose what kind of audio to generate
    generate_original = st.checkbox(
        "Generate original-language audio", value=True
    )
    generate_translated = st.checkbox(
        f"Generate translated audiobook audio ({target_language})",
        value=True,
    )

    accent = st.selectbox(
        "Select voice accent (approx.)",
        options=["com", "co.in", "co.uk", "com.au"],
        index=1,
        help="com = US, co.in = Indian, co.uk = British, com.au = Australian.",
    )

    slow_voice = st.checkbox("Use slower speech", value=False)

    generate_clicked = st.button("Generate Audiobooks")

    if generate_clicked:
        # If no audio type selected, warn and stop
        if not (generate_original or generate_translated):
            st.warning("Please select at least one audio type to generate.")
        elif uploaded_files:
            process_files(
                uploaded_files=uploaded_files,
                target_language=target_language,
                accent=accent,
                slow_voice=slow_voice,
                generate_original=generate_original,
                generate_translated=generate_translated,
            )
        else:
            st.warning("Please upload at least one file.")


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

        st.header(f"📄 {file_name}")

        try:
            raw_text = extract_text_any(file_name, file)
            if not raw_text.strip():
                st.error("No text could be extracted from this file.")
                continue

            st.subheader("Extracted Text (Preview)")
            st.text_area(
                "Raw text preview",
                raw_text[:2000],
                height=200,
                disabled=True,
            )

            chapters = split_into_chapters(raw_text)
            if not chapters:
                st.error("No chapters/content found after splitting.")
                continue

            st.success(f"Found {len(chapters)} chapter(s).")

            for ch_idx, ch_text in enumerate(chapters, start=1):
                st.markdown(f"## 🎧 Chapter {ch_idx}")

                # 1. Detect original language
                with st.spinner(f"Detecting language for Chapter {ch_idx}..."):
                    orig_lang_name, orig_tts_code = detect_language(ch_text)

                st.markdown(f"**Detected original language:** {orig_lang_name}")

                st.markdown("#### 📌 Actual Content (Original)")
                st.text_area(
                    f"Actual Text - Chapter {ch_idx}",
                    ch_text[:2000],
                    height=220,
                    disabled=True,
                )

                # 2. Translate + rephrase (we always need this for translated text)
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

                ch_base_name = f"{base_name}_chapter_{ch_idx}"

                # 3. Generate audio(s) depending on checkboxes
                orig_path = orig_bytes = None
                trans_path = trans_bytes = None

                if generate_original or generate_translated:
                    with st.spinner(
                        f"Generating selected audio for Chapter {ch_idx}..."
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

                # 4. Show players + download buttons conditionally

                if generate_original and orig_bytes:
                    st.markdown("##### 🔊 Original Audio")
                    st.audio(orig_bytes, format="audio/mp3")
                    st.download_button(
                        label=f"⬇️ Download Original Audio – Chapter {ch_idx}",
                        data=orig_bytes,
                        file_name=os.path.basename(orig_path),
                        mime="audio/mpeg",
                        key=f"download_orig_{ch_base_name}",
                    )

                if generate_translated and trans_bytes:
                    st.markdown(
                        f"##### 🎙 Translated Audiobook Audio ({target_language})"
                    )
                    st.audio(trans_bytes, format="audio/mp3")
                    st.download_button(
                        label=f"⬇️ Download Translated Audio – Chapter {ch_idx}",
                        data=trans_bytes,
                        file_name=os.path.basename(trans_path),
                        mime="audio/mpeg",
                        key=f"download_trans_{ch_base_name}",
                    )

        except Exception as e:
            st.error(f"Error processing {file_name}: {e}")


if __name__ == "__main__":
    main()
