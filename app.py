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
    # 1. LOAD THE MASTER DICTIONARY FROM RULES.TXT
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    # Extracts 'ModernWord' and '1860sWord'
                    parts = line.split("=")
                    modern = parts[0].strip().lower()
                    # Extracts the archive word before the (Meaning)
                    archive = parts[1].split("(")[0].strip()
                    rules_dict[modern] = archive

    # 2. THE HARD-SWAP: Python replaces words BEFORE the AI sees them
    # This stops the AI from using Modern Arabic like 'Latif'
    processed_text = user_input.lower()
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        # We use word boundaries \b to ensure we only replace whole words
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[word], processed_text)

    # 3. THE SCRIPTS LAWS: Forcing the Phonetic Frame
    system_instruction = """
    ROLE: 18th-century Cape Muslim Scribe.
    TASK: Transcribe the INPUT into Arabic Script using these EXACT LAWS:
    - Consonants: b=ب, p=پ, t=ت, s=ث, dj=ج, tj=چ, h=ح, ch=خ, d=د, r=ر, k=ك, l=ل, m=م, n=ن, w=و, j=ي.
    - Vowels: a=ـَ, aa=ـَا, i/ie=ـِي, o/oo=ـُ, u=ـُ, e/è=ـَِي.
    
    STRICT COMMAND: 
    1. NEVER use Modern Standard Arabic words.
    2. ONLY use the sounds provided in the input text.
    3. Output ONLY two lines: 1. Latin 1860s 2. Arabic Script.
    """

    for key in API_POOL:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash-lite',
                system_instruction=system_instruction
            )
            # Temperature 0 is mandatory to stop the AI from 'guessing'
            response = model.generate_content(
                f"TRANSCRIBE SOUNDS ONLY: {processed_text}",
                generation_config={"temperature": 0}
            )
            return response.text.strip()
        except Exception:
            continue
    return "❌ Connection error or keys exhausted."

# --- 3. UI LOGIC ---
user_input = st.text_area("Input:", height=100)
if st.button("EXECUTE"):
    if user_input:
        with st.spinner("Scribe is working..."):
            st.info(scribe_translator(user_input))
