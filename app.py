import streamlit as st
import google.generativeai as genai
import re
import os
import random

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Cape Arabic-Afrikaans Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Translator")

def scribe_translator(text_input):
    # --- STEP A: DICTIONARY EXTRACTION ---
    # Scans rules.txt for "Modern = Ancient" mappings to ensure 100% accuracy
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            content = f.read()
            # Matches "English/Modern = Cape/Arabic-Afrikaans"
            matches = re.findall(r'^([\w\s]+)\s*=\s*([\w\s\-]+)', content, re.MULTILINE)
            for key, val in matches:
                rules_dict[key.strip().lower()] = val.strip()

    # --- STEP B: PRE-PROCESS (Tier 1: Mandatory Phonology) ---
    processed = text_input.lower()
    
    # Apply primary phonological shifts from your sources
    processed = processed.replace("ui", "ei")      # Rule: ui > ei 
    processed = processed.replace("ge-", "ga-")    # Rule: ge- > ga- [cite: 6]
    processed = re.sub(r'([dt])\1', 'rr', processed) # Rule: dd/tt > rr [cite: 7]
    
    # Apply word-for-word Cape Mapping from rules_dict
    sorted_keys = sorted(rules_dict.keys(), key=len, reverse=True)
    for key in sorted_keys:
        pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
        processed = pattern.sub(rules_dict[key], processed)

    # --- STEP C: THE "IRONCLAD" SYSTEM INSTRUCTION ---
    # Instructs the AI to apply the exhaustive orthographic rules [cite: 94, 96]
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe (Abu Bakr Effendi tradition).
    STRICT ORTHOGRAPHY (Arabic Script):
    - CONSONANTS: 'p'=پ, 'g'(great)=گ, 'g/gh'(guttural)=خ, 'ng'=نگ, 'tj'=چ, 'dj'=ج, 'v/f'=ف[cite: 100, 101, 105, 108, 109].
    - VOWELS: Short 'a'=fatha, Long 'aa'=fatha+alif, 'ie'=kasra+ya, 'oe'=damma+waw[cite: 113, 114, 118, 119].
    - NO 'Z': Represent 'z' with 's' (س)[cite: 111].
    - NO TASHID: Do not double consonants using signs; write the letter twice[cite: 128].
    - EMPHATIC 'S': Use 'sad' (ص) ONLY for 'netsoes' or 'soes'[cite: 107].

    DICTIONARY PREFERENCE: {rules_dict}
    
    TASK: Translate the input. If a word is missing from the dictionary, use your brain to apply Cape Arabic-Afrikaans phonology rules (e.g., ui->ei, ge->ga, dd->rr)[cite: 5, 6, 7].
    """

    # --- STEP D: API POOL EXECUTION (Unlimited Logic) ---
    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: Add API keys to Streamlit Secrets."
    
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

    return "❌ All API keys exhausted. Add more keys for unlimited use."

# --- 3. UI EXECUTION ---
user_input = st.text_area("Enter sentence:", 
                         placeholder="e.g. He is reading the prayer after the fast", 
                         height=100)

if st.button("EXECUTE SCRIBE"):
    if user_input:
        with st.spinner("📜 Applying Scribe Laws..."):
            result = scribe_translator(user_input)
            st.info(result)
