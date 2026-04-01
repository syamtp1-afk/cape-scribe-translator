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
    # A. INITIALIZE & LOAD RULES
    processed_text = text_input.lower()
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
    OUTPUT: Two lines only. Line 1: Latin, Line 2: Arabic.
    """

    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: Add 'keys' list to Streamlit Secrets."

    # D. API POOL MANAGEMENT
    api_pool = list(st.secrets["keys"])
    random.shuffle(api_pool)
    
    # Use only the most stable model names
    models_to_try = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-8b']

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
                
                if response.text:
                    lines = [l.strip() for l in response.text.strip().split('\n') if l.strip()]
                    if len(lines) >= 2:
                        return f"**1. Latin:** {lines[0]}\n\n**2. Arabic:** {lines[1]}"
                    return response.text

            except Exception as e:
                # THIS IS THE SECRET SAUCE: Show the error for the first attempt
                st.warning(f"Attempt failed with {model_name}: {str(e)}")
                continue 

    return "❌ ALL ATTEMPTS EXHAUSTED. See warnings above for the specific error."

# --- 3. UI EXECUTION ---
user_input = st.text_area("Enter sentence:", height=100)
if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Consulting Archives..."):
            result = scribe_translator(user_input)
            st.info(result)
