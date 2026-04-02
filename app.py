import streamlit as st
import google.generativeai as genai
import re
import os
import random

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Cape Arabic-Afrikaans Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Translator")

def scribe_translator(text_input):
    # --- STEP A: CORE CAPE LEXICON (From provided sources) ---
    # These mappings ensure key cultural terms are never missed [cite: 32, 35, 71]
    cape_mapping = {
        "onions": "eiwe", "fast": "poewasa", "morning prayer": "soeboeg", 
        "mosque": "masiet", "read": "batcha", "thank you": "tramakasie",
        "please": "kanalla", "died": "gamaningal", "bath": "mannie",
        "after": "aghtir", "nobody": "ghaniemand", "on purpose": "aspris"
    }

    # --- STEP B: PRE-PROCESS PHONOLOGY & LEXICON ---
    processed = text_input.lower()
    
    # 1. Apply Hard-Coded Phonological Rules [cite: 5, 6, 7]
    processed = processed.replace("ui", "ei")      # ui > ei shift [cite: 5]
    processed = processed.replace("ge-", "ga-")    # ge- > ga- past tense [cite: 6]
    processed = re.sub(r'([dt])\1', 'rr', processed) # double d/t > rr (e.g. middag > marrag) [cite: 7]
    
    # 2. Apply Word-for-Word Cape Mapping [cite: 32, 71]
    for word, replacement in cape_mapping.items():
        processed = re.sub(rf'\b{word}\b', replacement, processed)

    # --- STEP C: THE "IRONCLAD" SYSTEM INSTRUCTION ---
    # Based on exhaustive orthographic and punctuation rules [cite: 94, 96]
    system_instruction = """
    ROLE: 19th-century Cape Muslim Scribe (Abu Bakr Effendi tradition).
    STRICT ORTHOGRAPHY (Arabic Script):
    - CONSONANTS: 'p'=پ, 'g'(great)=گ, 'g/gh'(guttural)=خ, 'ng'=نگ, 'tj'=چ, 'dj'=ج, 'v/f'=ف[cite: 98, 100, 105, 108, 109].
    - VOWELS: Short 'a'=fatha, Long 'aa'=fatha+alif, 'ie'=kasra+ya, 'oe'=damma+waw[cite: 113, 114, 118, 119].
    - NO 'Z': Represent 'z' with 's' (س)[cite: 111].
    - NO TASHID: Do not double consonants using signs; write the letter twice (e.g. 'wanier')[cite: 128].
    - EMPHATIC 'S': Use 'sad' (ص) ONLY for 'netsoes' or 'soes'[cite: 107].

    TASK: Convert the input into Latin (Phonetic Cape) and Arabic-Afrikaans script.
    FORMAT:
    Latin: [Cape Phonetic Transcription]
    Arabic: [Correct Arabic-Afrikaans Script]
    """

    # --- STEP D: API EXECUTION ---
    if "keys" not in st.secrets: return "❌ SETUP ERROR: Add API keys to Secrets."
    
    api_pool = list(st.secrets["keys"])
    random.shuffle(api_pool)
    
    for key in api_pool:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
            response = model.generate_content(f"Scribe this into Cape Arabic-Afrikaans: {processed}")
            return response.text
        except Exception: continue

    return "❌ All attempts failed. Check API connectivity or limits."

# --- UI EXECUTION ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. I am going to the mosque", height=100)
if st.button("EXECUTE SCRIBE"):
    if user_input:
        with st.spinner("📜 Writing in 19th-century Scribe..."):
            st.markdown(scribe_translator(user_input))
