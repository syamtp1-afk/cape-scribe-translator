import streamlit as st
import google.generativeai as genai
import re
import os

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

import streamlit as st
import google.generativeai as genai
import re
import os
import time
import random

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

def scribe_translator(text_input):
    # A. LOAD THE LAW
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    processed_text = text_input.lower()
    sorted_keys = sorted(rules_dict.keys(), key=len, reverse=True)
    for key in sorted_keys:
        pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[key], processed_text)

    # B. SYSTEM INSTRUCTION
    system_instruction = """
    ROLE: 19th-century Cape Muslim Scribe & Translator.
    TASK: Translate English to 1860s Cape Afrikaans, then convert to Arabic Script.
    ALPHABET: b=ب, p=پ, t=ت, s=س, dj=ج, tj=چ, h=ه, ch=خ, d=د, r=ر, sj=ش, f=ف, w=و, k=ك, g=گ, l=ل, m=م, n=ن, j=ي, ng=ڠ.
    Vowels: a=ـَ, aa=ـَا, i/ie=ـِي, o/oo=ـُ, oe=ـُو, e=ـِ.
    OUTPUT: Two lines only. Line 1: Latin, Line 2: Arabic.
    """

    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: Add 'keys' list to Streamlit Secrets."

    # C. API POOL MANAGEMENT
    api_pool = list(st.secrets["keys"])
    random.shuffle(api_pool) # Spread the load across keys
    
    # Try multiple models in case one is throttled
    models_to_try = ['gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash-8b']

    for key in api_pool:
        genai.configure(api_key=key.strip())
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name, 
                    system_instruction=system_instruction
                )
                
                response = model.generate_content(
                    f"Process: {processed_text}", 
                    generation_config={"temperature": 0.2}
                )
                
                lines = [l.strip() for l in response.text.strip().split('\n') if l.strip()]
                if len(lines) >= 2:
                    return f"**1. Latin 1860s transcription:** {lines[0]}\n\n**2. Arabic script version:** {lines[1]}"
                return f"**Result:**\n{response.text}"

            except Exception as e:
                err_msg = str(e).lower()
                if "429" in err_msg or "quota" in err_msg:
                    time.sleep(1) # Wait a second before trying next model/key
                    continue 
                else:
                    return f"❌ API Error: {str(e)}"

    return "❌ ALL KEYS EXHAUSTED. Please wait 60 seconds and try again."

# --- 3. UI EXECUTION ---
try:
    user_input = st.text_area("Enter sentence:", height=100)
    if st.button("EXECUTE"):
        if user_input:
            with st.spinner("📜 Rotating API Keys & Consulting Archives..."):
                result = scribe_translator(user_input)
                st.info(result)
except Exception as e:
    st.error(f"Critical Error: {e}")

# --- 3. UI EXECUTION ---
# Wrapping in a try block to prevent the "Blank Screen of Death"
try:
    user_input = st.text_area("Enter sentence:", placeholder="e.g. you are cute", height=100)

    if st.button("EXECUTE"):
        if user_input:
            with st.spinner("📜 Consulting Archive Laws..."):
                result = scribe_translator(user_input)
                st.info(result)
        else:
            st.warning("Please enter text first.")
except Exception as e:
    st.error(f"Critical App Error: {e}")
