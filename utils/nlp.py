# utils/nlp.py

import os
from typing import Tuple

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in .env")

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-2.5-flash"

SUPPORTED_LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Marathi": "mr",
    "Tamil": "ta",
    "Telugu": "te",
    "Bengali": "bn",
    "Gujarati": "gu",
}


def detect_language(text: str) -> Tuple[str, str]:
    """
    Detect language from text using Gemini.
    Returns (language_name, tts_code).
    """
    if not text.strip():
        return "English", "en"

    prompt = (
        "Detect the language of the text below. "
        "Answer using ONLY ONE WORD from this list: "
        "English, Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati.\n\n"
        f"TEXT:\n{text[:1500]}"
    )

    model = genai.GenerativeModel(MODEL_NAME)
    resp = model.generate_content(prompt)
    raw = (resp.text or "").strip()

    lang_name = raw.split()[0].strip().capitalize()
    if lang_name not in SUPPORTED_LANGUAGES:
        lang_name = "English"

    return lang_name, SUPPORTED_LANGUAGES[lang_name]


def translate_and_rephrase(text: str, target_language: str) -> str:
    """
    Translate text into target_language and rephrase in audiobook style.
    target_language is a key from SUPPORTED_LANGUAGES, e.g. 'Hindi'.
    """
    if not text.strip():
        return ""

    if target_language not in SUPPORTED_LANGUAGES:
        target_language = "English"

    prompt = (
        f"You are an expert translator and audiobook narrator.\n"
        f"1. Translate the following text into {target_language}.\n"
        f"2. Rewrite it as a smooth, engaging audiobook narration.\n"
        f"3. Keep the meaning accurate. Do NOT add new facts.\n"
        f"4. Return ONLY the final narrated text in {target_language}.\n\n"
        f"TEXT:\n{text}"
    )

    model = genai.GenerativeModel(MODEL_NAME)
    resp = model.generate_content(prompt)
    return (resp.text or "").strip()
