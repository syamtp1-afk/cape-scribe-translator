import streamlit as st
import google.generativeai as genai
import re
import os
import random

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

def scribe_translator(text_input):
    processed_text = text_input.lower()
    
    # [Rules logic remains the same]
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

    # 1. FORCE THE VERSION (Add this line before model initialization)
    # This prevents the "v1beta" 404 error
    os.environ["GOOGLE_API_USE_MTLS"] = "never" 

    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: Add 'keys' list to Streamlit Secrets."

    api_pool = list(st.secrets["keys"])
    random.shuffle(api_pool)
    
    # 2. USE FULL STRINGS WITH NO 'models/' PREFIX
    # Sometimes the SDK is very sensitive to the leading slash
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro']

    for key in api_pool:
        try:
            genai.configure(api_key=key.strip())
            
            for model_name in models_to_try:
                try:
                    # 3. INITIALIZE WITHOUT SYSTEM_INSTRUCTION FIRST
                    # Older API versions crash when system_instruction is passed
                    model = genai.GenerativeModel(model_name=model_name)
                    
                    prompt = f"""
                    ROLE: 19th-century Cape Muslim Scribe.
                    TASK: Translate to 1860s Cape Afrikaans + Arabic Script.
                    INPUT: {processed_text}
                    OUTPUT: Two lines (Latin then Arabic).
                    """
                    
                    response = model.generate_content(prompt)
                    
                    if response.text:
                        return response.text

                except Exception as inner_e:
                    st.warning(f"Model {model_name} failed: {inner_e}")
                    continue
        except Exception as outer_e:
            st.warning(f"Key failed: {outer_e}")
            continue

    return "❌ All attempts failed. Check your Streamlit requirements.txt for 'google-generativeai'."

# --- UI EXECUTION ---
user_input = st.text_area("Enter sentence:", height=100)
if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Consulting Archives..."):
            result = scribe_translator(user_input)
            st.info(result)
