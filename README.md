# 🎧 **Multilingual AI Audiobook Generator**

🔗 **Live Demo:**  
https://rajpal18-ai-based-auido-generator-app-h96ltx.streamlit.app/

The **Multilingual AI Audiobook Generator** allows users to upload **PDF / DOCX / TXT** documents and automatically convert them into **audiobook-style MP3 narration**.

---

## 🚀 **Key Features**
- Upload **PDF / DOCX / TXT**
- **Automatic language detection**
- **Chapter-wise processing**
- Generate two types of audio:
  - 🔊 Original-language narration
  - 🌍 Translated & rephrased audiobook narration
- **Supports 7 output languages:**
  - English, Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati
- User-friendly **Streamlit interface**
- **MP3 download per chapter**

---

## 🧠 **Technology Stack**
| Layer | Technology |
|-------|-------------|
| Frontend | Streamlit |
| Text Extraction | PyPDF2, python-docx |
| NLP | Google Gemini |
| TTS | gTTS |
| Secrets Handling | python-dotenv |
| Language Detection & Rewriting | Gemini NLP |

---

## 📂 **Project Structure**
```
project_root/
│ app.py
│ requirements.txt
│ .gitignore
│ README.md
│
├─ utils/
│   extract_text.py
│   chapters.py
│   nlp.py
│   tts.py
│
├─ assets/
│   banner.png
│
└─ outputs/
    └─ audio/    (generated MP3 files)
```

---

## ⚙ **Setup & Installation**

### ① Install dependencies
```bash
pip install -r requirements.txt
```

### ② Add your Gemini API key
Create a file named `.env` (do NOT upload to GitHub):
```
GEMINI_API_KEY=your_api_key_here
```

### ③ Run the app
```bash
streamlit run app.py
```

---

## ▶ **How It Works**
1. Upload document(s)
2. Text automatically extracted
3. Split into chapters
4. Detect original language using AI
5. Translate + rewrite in audiobook style
6. Generate MP3 audio (original & translated)
7. Play or download MP3 chapter-wise

---

## 📌 **Functional Requirements**
- Document upload
- Automatic language detection
- Translation + narration option
- Text-to-speech generation
- Downloadable MP3 output

## 📌 **Non-Functional Requirements**
- Easy to use UI
- Secure API key handling
- Fast audio generation (depends on chapter length)
- Works across operating systems
- Modular & maintainable code

---

## 🔐 **Security Notes**
- `.env` must NOT be uploaded to GitHub
- Audio files and temporary directories should be ignored
- Use **Streamlit Secrets** when deploying to cloud

---

## 👨‍💻 **Developer**
**Rajpal Rajput**  
B.Tech — AI & Data Science

---

## 📬 **Future Scope**
- Neural TTS voices (OpenAI / Azure)
- Full audiobook MP3 merger
- Background music in audio
- EPUB / website article support
- Download complete audiobook ZIP

---

## 💡 **Live Demo**
👉 https://rajpal18-ai-based-auido-generator-app-h96ltx.streamlit.app/

---

### ⭐ If this project helped you  
Consider giving the repo a **Star ⭐ on GitHub**!
