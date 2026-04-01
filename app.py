import streamlit as st
import google.generativeai as genai
import re
import os
import time
import random

# 1. UI SETUP (Must be first and only once)
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

def scribe_translator(text_input):
    # Initialize the variable immediately to avoid "not defined" errors
    processed_text = text_input.lower() 
    
    # A. LOAD THE RULES
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # B. APPLY RULES
    sorted_keys = sorted(rules_dict.keys(), key=len, reverse=True)
    for key in sorted_keys:
        pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[key], processed_text)

    # C. SYSTEM INSTRUCTION
    system_instruction = """
    ROLE: 19th-century Cape Muslim Scribe & Translator.
    TASK: Translate English to 1860s Cape Afrikaans, then convert to Arabic Script.
    ALPHABET: b=ب, p=پ, t=ت, s=س, dj=ج, tj=چ, h=ه, ch=خ, d=د, r=ر, sj=ش, f=ف, w=و, k=ك, g=گ, l=ل, m=م, n=ن, j=ي, ng=ڠ.
    Vowels: a=ـَ, aa=ـَا, i/ie=ـِي, o/oo=ـُ, oe=ـُو, e=ـِ.
    OUTPUT: Two lines only. Line 1: Latin, Line 2: Arabic.
    """

    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: Add 'keys' list to Streamlit Secrets."

    # D. API EXECUTION
    api_pool = list(st.secrets["keys"])
    random.shuffle(api_pool)
    
    # Using 'models/' prefix to fix your previous 404 error
    models_to_try = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-8b']

    for key in api_pool:
        genai.configure(api_key=key.strip())
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name, 
                    system_instruction=system_instruction
                )
                
                # 'processed_text' is definitely defined by now
                response = model.generate_content(f"Process: {processed_text}")
                
                if response.text:
                    return response.text
            except Exception as e:
                continue # Try next model/key

    return "❌ All attempts failed. Check logs."

# 3. UI EXECUTION
user_input = st.text_area("Enter sentence:", height=100)
if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Processing..."):
            result = scribe_translator(user_input)
            st.info(result)
