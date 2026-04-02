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
    # Automatically pulls "Modern = Ancient" mappings from rules.txt
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            content = f.read()
            # Matches patterns like "onions = eiwe" or "fasting = poewasa"
            matches = re.findall(r'^([\w\s]+)\s*=\s*([\w\s\-]+)', content, re.MULTILINE)
            for key, val in matches:
                rules_dict[key.strip().lower()] = val.strip()

    # --- STEP B: PRE-PROCESS (Tier 1: Mandatory Phonology) ---
    processed = text_input.lower()
    
    # Apply Standard Phonological Shifts from your sources
    processed = processed.replace("ui", "ei")      # Rule: ui > ei [cite: 5]
    processed = processed.replace("ge-", "ga-")    # Rule: ge- > ga- [cite: 6]
    processed = re.sub(r'([dt])\1', 'rr', processed) # Rule: dd/tt > rr [cite: 7]
    
    # Apply word-for-word Cape Mapping
    sorted_keys = sorted(rules_dict.keys(), key=len, reverse=True)
    for key in sorted_keys:
        pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
        processed = pattern.sub(rules_dict[key], processed)

    # --- STEP C: THE SCRIBE BRAIN (Tier 2: AI Orthography) ---
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe (Abu Bakr Effendi tradition).
    STRICT ORTHOGRAPHY (Arabic Script):
    - CONSONANTS: 'p'=پ, 'g'(great)=گ, 'g/gh'(guttural)=خ, 'ng'=نگ, 'tj'=چ, 'dj'=ج, 'v/f'=ف[cite: 22, 23, 24, 25, 26].
    - VOWELS: Short 'a'=fatha, Long 'aa'=fatha+alif, 'ie'=kasra+ya, 'oe'=damma+waw[cite: 15, 16, 17, 18].
    - NO 'Z': Use 's' (س)[cite: 27, 28].
    - NO TASHID: Write letters twice instead of using the doubling sign[cite: 29].
    - EMPHATIC 'S': Use 'sad' (ص) ONLY for 'netsoes' or 'soes'[cite: 28].

    DICTIONARY: {rules_dict}
    
    TASK: Translate the input. If a word is missing from the dictionary, apply your AI brain to follow the 1860s Cape phonology and orthography.
    """

    # --- STEP D: UNLIMITED API POOL ---
    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: Add API keys to Streamlit Secrets."
    
    api_pool = list(st.secrets["keys"])
    random.shuffle(api_pool) # Randomize to distribute load
    
    for key in api_pool:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
            response = model.generate_content(f"Scribe this exactly: {processed}")
            return response.text
        except Exception:
            continue # Try the next key if one fails/limits
            
    return "❌ All API keys exhausted. Please add more keys to Secrets for unlimited use."

# --- UI EXECUTION ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. He is reading the prayer after the fast", height=100)
if st.button("EXECUTE SCRIBE"):
    if user_input:
        with st.spinner("📜 Applying Scribe Laws..."):
            st.info(scribe_translator(user_input))
