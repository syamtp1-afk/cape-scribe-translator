import streamlit as st
import google.generativeai as genai
import re
import os
import random

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Cape Arabic-Afrikaans Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Translator")

def scribe_translator(text_input):
    # --- STEP A: DICTIONARY LOOKUP ---
    # Manually defined from your exhaustive source text to ensure 100% accuracy
    cape_lexicon = {
        "onions": "eiwe", "nobody": "ghaniemand", "mosque": "masiet", 
        "fast": "poewasa", "morning prayer": "soeboeg", "read": "batcha",
        "after": "aghtir", "wait": "aitwagh", "thank you": "tramakasie",
        "please": "kanalla", "died": "gamaningal", "bath": "mannie"
    }

    # --- STEP B: PRE-PROCESS PHONOLOGY (Tier 1) ---
    # Applying the core Cape Muslim Afrikaans shifts [cite: 5, 7]
    processed = text_input.lower()
    processed = processed.replace("ui", "ei")  # ui > ei 
    processed = processed.replace("ge-", "ga-") # ge- > ga- [cite: 6]
    
    # Replace modern words with Cape Lexicon
    for word, replacement in cape_lexicon.items():
        processed = re.sub(rf'\b{word}\b', replacement, processed)

    # --- STEP C: THE SCRIBE SYSTEM INSTRUCTION (Tier 2) ---
    # Instruction based on the Exhaustive Orthographic Rules [cite: 94, 96]
    system_instruction = """
    ROLE: 19th-century Cape Muslim Scribe (Abu Bakr Effendi tradition).
    STRICT ORTHOGRAPHY (Arabic Script):
    1. CONSONANTS: 'p'=پ, 'g'(great)=گ, 'g/gh'(guttural)=خ, 'ng'=نگ, 'tj'=چ, 'dj'=ج, 'v/f'=ف[cite: 23, 24, 25, 26, 27].
    2. VOWELS: Short 'a'=fatha, Long 'aa'=fatha+alif, 'ie'=kasra+ya, 'oe'=damma+waw[cite: 15, 16, 17, 18].
    3. NO 'Z': Always use 's' (س)[cite: 28, 111].
    4. NO TASHID: Never use the doubling sign; write letters twice if needed (e.g. 'wanier')[cite: 30, 128].
    5. INITIAL VOWELS: Must start with an Alif carrier[cite: 31, 112].

    TASK: Convert the input into Latin (Phonetic) and Arabic-Afrikaans script.
    FORMAT:
    Latin: [Cape Phonetic]
    Arabic: [Arabic Script]
    """

    # --- STEP D: EXECUTION ---
    if "keys" not in st.secrets: return "❌ Add API keys to Streamlit Secrets."
    
    api_pool = list(st.secrets["keys"])
    random.shuffle(api_pool)
    
    for key in api_pool:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
            response = model.generate_content(f"Scribe this into Cape Arabic-Afrikaans: {processed}")
            return response.text
        except Exception: continue

    return "❌ Translation failed. Check API connectivity."

# --- UI EXECUTION ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. I am going to the mosque", height=100)
if st.button("EXECUTE SCRIBE"):
    if user_input:
        with st.spinner("📜 Writing in 19th-century Scribe..."):
            st.info(scribe_translator(user_input))
