import streamlit as st
import google.generativeai as genai
import re
import os

# --- 1. UI SETUP ---
st.set_page_config(page_title="Master Scribe 1860", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

# --- 2. KEY POOL ---
API_POOL = st.secrets.get("keys", [])
def scribe_translator(user_input):
    # 1. LOAD THE DICTIONARY FROM RULES.TXT
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    modern = parts[0].strip().lower()
                    # Capture the 1860s Cape word only
                    archive = parts[1].split("(")[0].strip()
                    rules_dict[modern] = archive

    # 2. THE HARD INTERCEPTOR: Python forces the change
    # This stops the AI from seeing 'how' and producing 'هَاو'
    processed_text = user_input.lower()
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        # \b ensures we only replace full words, not parts of words
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[word], processed_text)

    # 3. THE SCRIPT BRAIN: Dedicated Phonetic Framing
    system_instruction = """
    ROLE: 18th-century Cape Muslim Scribe.
    TASK: Transcribe the INPUT into Arabic Script using these EXACT LAWS:
    - Consonants: b=ب, p=پ, t=ت, s=ث, dj=ج, tj=چ, h=ح, ch=خ, d=د, r=ر, k=ك, l=ل, m=م, n=ن, w=و, j=ي, g=غ, v/f=ف.
    - Vowels: a=ـَ, aa=ـَا, i/ie=ـِي, o/oo=ـُ, u=ـُ, e/è=ـَِي.
    
    STRICT COMMAND: 
    1. NEVER transcribe modern English phonetics (e.g., 'how' -> 'هَاو' is FORBIDDEN).
    2. ONLY use the sounds of the CAPE words provided in the input.
    3. Output ONLY two lines: 1. Latin 1860s 2. Arabic Script.
    """

    for key in API_POOL:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash-lite',
                system_instruction=system_instruction
            )
            # Temperature 0: The Absolute Accuracy Lock
            response = model.generate_content(
                f"TEXT: {processed_text}",
                generation_config={"temperature": 0}
            )
            return response.text.strip()
        except Exception:
            continue
    return "❌ All Keys Exhausted."

# --- 3. UI LOGIC ---
user_input = st.text_area("Input:", height=100)
if st.button("EXECUTE"):
    if user_input:
        with st.spinner("Scribe is working..."):
            st.info(scribe_translator(user_input))
