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
    processed_text = text_input.lower()
    rules_dict = {}
    
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    sorted_keys = sorted(rules_dict.keys(), key=len, reverse=True)
    for key in sorted_keys:
        pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[key], processed_text)

    system_instruction = (
        "ROLE: 19th-century Cape Muslim Scribe & Translator. "
        "TASK: Translate English to 1860s Cape Afrikaans, then convert to Arabic Script. "
        "OUTPUT: Two lines only. Line 1: Latin, Line 2: Arabic."
    )

    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: Add 'keys' list to Streamlit Secrets."

    api_pool = list(st.secrets["keys"])
    random.shuffle(api_pool)
    
    # Try the names WITHOUT 'models/' prefix - the SDK often adds it automatically
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemini-1.5-pro']

    for key in api_pool:
        # Step 1: Force standard configuration
        genai.configure(api_key=key.strip())
        
        for model_name in models_to_try:
            try:
                # Step 2: Initialize model
                model = genai.GenerativeModel(
                    model_name=model_name, 
                    system_instruction=system_instruction
                )
                
                # Step 3: Simple call
                response = model.generate_content(f"Translate: {processed_text}")
                
                if response.text:
                    return response.text

            except Exception as e:
                # Log the error for visibility
                st.warning(f"Skipping {model_name} on this key due to: {e}")
                continue 

    return "❌ All keys/models failed. Please check if your API keys are active in Google AI Studio."

# --- UI EXECUTION ---
user_input = st.text_area("Enter sentence:", height=100)
if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Consultating Archives..."):
            result = scribe_translator(user_input)
            st.info(result)
