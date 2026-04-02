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
    # We use a robust regex to pull "Modern = Ancient" from your text file
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            content = f.read()
            # Finds lines like "onions = eiwe" or "fast = poewasa"
            matches = re.findall(r'^([\w\s]+)\s*=\s*([\w\s\-]+)', content, re.MULTILINE)
            for key, val in matches:
                rules_dict[key.strip().lower()] = val.strip()

    # --- STEP B: PRE-PROCESS (Tier 1: Historical Mapping) ---
    processed = text_input.lower()
    sorted_keys = sorted(rules_dict.keys(), key=len, reverse=True)
    for key in sorted_keys:
        pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
        processed = pattern.sub(rules_dict[key], processed)

    # --- STEP C: THE SCRIBE BRAIN (Tier 2: Generative AI) ---
    # This system instruction forces the AI to "think" like an 1860s Cape Muslim scholar
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe (Abu Bakr Effendi tradition).
    CONTEXT: You are translating into 'Arabic-Afrikaans' (Cape Muslim dialect).
    
    STRICT LINGUISTIC LAWS:
    1. PHONOLOGY: Double 'd' or 't' becomes 'rr' (middag > marrag). 'ui' becomes 'ei' (uiwe > eiwe). Past tense prefix is 'ga-' (ga-maak).
    2. ARABIC ORTHOGRAPHY: 
       - Consonants: P=پ, G(great)=گ, G(guttural)=خ, NG=نگ, TJ=چ, DJ=ج, V/F=ف.
       - Vowels: Short 'a'=fatha, Long 'aa'=fatha+alif, 'ie'=kasra+ya, 'oe'=damma+waw.
    3. NO 'Z' OR TASHID: Never use 'z' (use 's') or the doubling sign (write letter twice).
    4. SYNTAX: Use Afrikaans Subject-Object-Verb (SOV) order.
    
    DICTIONARY (PRIORITIZE):
    {rules_dict}
    
    TASK: Translate the input. If a word isn't in the dictionary, use your AI brain to apply the 1860s Cape phonology rules to create a period-accurate transcription.
    
    OUTPUT FORMAT:
    Latin: [Cape Phonetic]
    Arabic: [Arabic-Afrikaans Script]
    """

    # --- STEP D: API POOL EXECUTION ---
    if "keys" not in st.secrets: return "❌ ERROR: Add API keys to Secrets."
    api_pool = list(st.secrets["keys"])
    random.shuffle(api_pool)
    
    for key in api_pool:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
            response = model.generate_content(f"Scribe this: {processed}")
            return response.text
        except Exception: continue
    return "❌ API Limit reached. Add more keys for unlimited use."

# --- UI EXECUTION ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. He is reading the prayer after the fast", height=100)
if st.button("EXECUTE SCRIBE"):
    if user_input:
        with st.spinner("📜 Writing in 19th-century Scribe..."):
            st.info(scribe_translator(user_input))
