import streamlit as st
import google.generativeai as genai
import re
import os
import time

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

# --- 2. THE ENGINE ---
def scribe_translator(text_input):
    # A. LOAD THE LAW (rules.txt)
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # B. HARD-SWAP (Python Pre-Processor)
    processed_text = text_input.lower()
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[word], processed_text)

    # C. SYSTEM INSTRUCTION
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    TASK: Convert 1860s Latin to 1860s Arabic Script.
    STRICT RULE: DO NOT change spellings. Use this map:
    b=ب, p=پ, t=ت, s=ث, dj=ج, tj=چ, h=ح, ch=خ, d=د, r=ر, sj=ش, f=ف, w=و, k=ك, g=گ, l=ل, m=م, n=ن, j=ي
    Vowels: a=ـَ, aa=ـَا, ie=ـِي, oe=ـُ, oo=ـَُو, e=ـَِ
    """

    # D. MULTI-KEY & AUTO-MODEL FAILOVER
    try:
        api_keys = st.secrets["keys"]
    except:
        return "❌ SETUP ERROR: 'keys' not found in Secrets."

    # UPDATED 2026 MODEL LIST (Priority Order)
    model_options = ["gemini-3-flash-preview", "gemini-2.5-flash", "gemini-2.5-flash-lite"]

    for key in api_keys:
        genai.configure(api_key=key.strip())
        for model_name in model_options:
            try:
                model = genai.GenerativeModel(model_name, system_instruction=system_instruction)
                response = model.generate_content(f"CONVERT: {processed_text}", generation_config={"temperature": 0})
                
                # If we get here, it worked!
                return f"**Latin 1860s transcription:** {processed_text}\n\n**Arabic script version:** {response.text.strip()}"
            except Exception as e:
                # If 404, try next model. If 429, try next key.
                continue

    return "❌ CRITICAL: All 2026 models and keys failed. Check API billing/status."

# --- 3. MAIN UI ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. how are you", height=100)

if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Consulting Archive..."):
            result = scribe_translator(user_input)
            st.info(result)
    else:
        st.warning("Please enter text.")

st.divider()
st.caption("Universal Scribe Engine v7.0 | 2026 Model Patch | Strict Word Swap")
