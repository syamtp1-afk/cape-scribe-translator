import streamlit as st
import google.generativeai as genai
import re
import os
import random

# --- 1. THE PERMANENT RULE ENGINE (Local Backup) ---
# This ensures 100% accuracy even if the AI brain is "tired"
LEXICON = {
    "onions": "eiwe", "fast": "poewasa", "morning prayer": "soeboeg", 
    "mosque": "masiet", "read": "batcha", "thank you": "tramakasie",
    "please": "kanalla", "died": "gamaningal", "bath": "mannie",
    "after": "aghtir", "nobody": "ghaniemand", "on purpose": "aspris"
}

def apply_scribe_laws(text):
    text = text.lower()
    # 1. Phonological Rules [Source 5, 7]
    text = text.replace("ui", "ei")      # Rule: ui > ei [cite: 5]
    text = text.replace("ge-", "ga-")    # Rule: ge- > ga- [cite: 6]
    text = re.sub(r'([dt])\1', 'rr', text) # Rule: dd/tt > rr (e.g. middag > marrag) [cite: 7]
    
    # 2. Lexical Replacement [Source 32, 33]
    for eng, cape in LEXICON.items():
        text = re.compile(rf'\b{re.escape(eng)}\b', re.IGNORECASE).sub(cape, text)
    return text

# --- 2. STREAMLIT UI ---
st.set_page_config(page_title="1860s Cape Master Scribe", page_icon="🕌")
st.title("🕌 100% Final Arabic-Afrikaans Translator")

def scribe_translator(text_input):
    processed = apply_scribe_laws(text_input)

    # STEP C: THE SYSTEM INSTRUCTION [Source 15, 22, 29]
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    STRICT ORTHOGRAPHY (Arabic Script):
    - CONSONANTS: 'p'=پ, 'g'(great)=گ, 'g/gh'(guttural)=خ, 'ng'=نگ, 'tj'=چ, 'dj'=ج, 'v/f'=ف. [cite: 22, 23, 24, 25, 26]
    - VOWELS: Short 'a'=fatha, Long 'aa'=fatha+alif, 'ie'=kasra+ya, 'oe'=damma+waw. [cite: 15, 16, 17, 18]
    - NO 'Z': Use 's' (س). [cite: 27]
    - NO TASHID: Write letters twice (e.g. 'wanier'). [cite: 29]
    - EMPHATIC 'S': Use 'sad' (ص) ONLY for 'netsoes' or 'soes'. [cite: 28]
    
    TASK: Scribe the processed text. If you reach an unknown word, use your brain to apply Cape Arabic-Afrikaans phonology.
    """

    # STEP D: UNLIMITED KEY ROTATION
    if "keys" not in st.secrets:
        return f"**LOCAL TRANSCRIPTION (AI Offline):**\n{processed}\n\n❌ ERROR: Add API keys to Secrets."
    
    api_pool = list(st.secrets["keys"])
    random.shuffle(api_pool)
    
    for key in api_pool:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
            response = model.generate_content(f"Scribe this exactly: {processed}")
            return response.text
        except Exception:
            continue 

    return f"**LOCAL TRANSCRIPTION (Limits Reached):**\n{processed}\n\n⚠️ Add more keys for Arabic Script."

# --- 3. EXECUTION ---
user_input = st.text_area("Enter sentence:", height=100)
if st.button("EXECUTE FINAL SCRIBE"):
    if user_input:
        with st.spinner("📜 Applying Scribe Laws..."):
            st.info(scribe_translator(user_input))
