import streamlit as st
import google.generativeai as genai
import re
import os
import time

# --- 1. SETTINGS & UI ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

# --- 2. THE ULTIMATE ENGINE ---
def scribe_translator(text_input):
    # A. LOAD THE LAW (rules.txt)
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # B. THE HARD INTERCEPT (Python Layer)
    processed_text = text_input.lower()
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[word], processed_text)

    # C. SCRIPT LOGIC (The Alphabet)
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    TASK: Convert the following 1860s Latin text into 1860s Arabic Script.
    STRICT RULE: DO NOT change the spelling of the Latin text. Use ONLY the mapping provided.
    
    ALPHABET:
    b=ب, p=پ, t=ت, s=ث, dj=ج, tj=چ, h=ح, ch=خ, d=د, r=ر, sj=ش, f=ف, w=و, k=ك, g=گ, l=ل, m=م, n=ن, j=ي
    Vowels: a=ـَ, aa=ـَا, ie=ـِي, oe=ـُ, oo=ـَُو, e=ـَِ
    
    LATIN INPUT: {processed_text}
    """

    # D. MULTI-KEY FAILOVER & MODEL AUTODETECT
    try:
        api_keys = st.secrets["keys"]
    except:
        return "❌ ERROR: 'keys' list not found in Streamlit Secrets."

    # Try these models in order to prevent 404 errors
    model_names = ["gemini-1.5-flash", "gemini-pro"]

    for key in api_keys:
        for model_name in model_names:
            try:
                genai.configure(api_key=key.strip())
                model = genai.GenerativeModel(model_name, system_instruction=system_instruction)
                
                response = model.generate_content(
                    f"Convert this to Arabic Script: {processed_text}", 
                    generation_config={"temperature": 0}
                )
                
                # Return the result and stop everything if successful
                return f"**Latin 1860s transcription:** {processed_text}\n\n**Arabic script version:** {response.text.strip()}"
                
            except Exception as e:
                # If it's a 404, the inner loop tries the next model name
                # If it's a 429 (rate limit), the outer loop tries the next key
                continue 

    return "❌ CRITICAL: All keys and models failed. Check your API dashboard."

# --- 3. UI LAYOUT ---
# Define variable BEFORE the button to prevent NameError
user_input = st.text_area("Enter sentence:", placeholder="e.g. how are you", height=100)

if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Consulting Archive Laws..."):
            result = scribe_translator(user_input)
            st.info(result)
    else:
        st.warning("Please enter text first.")

st.divider()
st.caption("Universal Scribe Engine v6.0 | Fix: Model 404 Autodetect & Strict Swap")
