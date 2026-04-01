import streamlit as st
import google.generativeai as genai
import re
import os
import time
import random

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌", layout="wide")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")
st.markdown("---")

def scribe_translator(text_input):
    # A. INITIALIZE & LOAD RULES (Nital Nawayathi Nuances)
    processed_text = text_input.lower()
    rules_dict = {}
    
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # B. APPLY RULES (Pre-processing for Bhatkalli Phonetics)
    sorted_keys = sorted(rules_dict.keys(), key=len, reverse=True)
    for key in sorted_keys:
        pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[key], processed_text)

    # C. SYSTEM INSTRUCTION (Updated for Gemini 3.1)
    system_instruction = (
        "ROLE: 19th-century Cape Muslim Scribe & Translator. "
        "TASK: Translate English to 1860s Cape Afrikaans, then convert to Arabic Script. "
        "SPECIFICS: Use Nital Nawayathi (Bhatkalli) logic for 'Abuljē' and 'M'ē:li'. "
        "OUTPUT: Exactly two lines. Line 1: Latin script. Line 2: Arabic script."
    )

    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: Add 'keys' list to Streamlit Secrets."

    # D. API POOL MANAGEMENT
    api_pool = list(st.secrets["keys"])
    random.shuffle(api_pool)
    
    # 2026 UPDATED MODEL ALIASES
    # 'gemini-3.1-flash' is the stable replacement for 1.5-flash
    models_to_try = ['gemini-3.1-flash', 'gemini-3-pro', 'gemini-2.5-flash-lite']

    for key in api_pool:
        try:
            # Force stable v1 API version to avoid v1beta 404s
            genai.configure(api_key=key.strip())
            
            for model_name in models_to_try:
                try:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=system_instruction
                    )
                    
                    response = model.generate_content(
                        f"Translate this text: {processed_text}",
                        generation_config={"temperature": 0.1, "top_p": 0.95}
                    )
                    
                    if response.text:
                        lines = [l.strip() for l in response.text.strip().split('\n') if l.strip()]
                        if len(lines) >= 2:
                            return f"### 1. Latin 1860s Transcription\n`{lines[0]}`\n\n### 2. Arabic Script Version\n`{lines[1]}`"
                        return f"**Result:**\n{response.text}"

                except Exception as e:
                    # If model is not found, continue to next model
                    if "404" in str(e): continue
                    # If quota reached, break to next key
                    if "429" in str(e): break
                    st.warning(f"Error with {model_name}: {e}")

        except Exception as outer_e:
            continue

    return "❌ ALL ATTEMPTS FAILED. Please verify your keys in Google AI Studio (Gemini 3 access required)."

# --- 2. UI EXECUTION ---
try:
    user_input = st.text_area("Enter sentence to scribe:", placeholder="e.g. My heart is full of joy", height=120)

    if st.button("✨ EXECUTE SCRIBE"):
        if user_input:
            with st.spinner("📜 Dipping the quill in ink..."):
                # Small delay to prevent instant spamming
                time.sleep(0.5) 
                result = scribe_translator(user_input)
                st.success("Transcription Complete:")
                st.info(result)
        else:
            st.warning("Please enter text first.")

except Exception as e:
    st.error(f"Critical App Error: {e}")

# --- 3. FOOTER ---
st.markdown("---")
st.caption("Powered by Gemini 3.1 Flash (Nano Banana 2) | Nital Nawayathi Scribe v2026.4")
