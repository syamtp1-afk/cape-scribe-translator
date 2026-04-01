import streamlit as st
import google.generativeai as genai
import re
import os

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

def scribe_translator(text_input):
    # ... (Keep your Rules A logic as is) ...

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

    api_pool = list(st.secrets["keys"])
    random.shuffle(api_pool)
    
    # CORRECTED MODEL NAMES WITH PREFIXES
    models_to_try = [
        'models/gemini-1.5-flash', 
        'models/gemini-1.5-flash-8b',
        'models/gemini-1.5-pro' 
    ]

    for key in api_pool:
        genai.configure(api_key=key.strip())
        
        for model_name in models_to_try:
            try:
                # The model initialization
                model = genai.GenerativeModel(
                    model_name=model_name, 
                    system_instruction=system_instruction
                )
                
                response = model.generate_content(
                    f"Process: {processed_text}", 
                    generation_config={"temperature": 0.2}
                )
                
                # Check if response has text (to avoid safety filter blocks)
                if response.text:
                    lines = [l.strip() for l in response.text.strip().split('\n') if l.strip()]
                    if len(lines) >= 2:
                        return f"**1. Latin 1860s transcription:** {lines[0]}\n\n**2. Arabic script version:** {lines[1]}"
                    return f"**Result:**\n{response.text}"

            except Exception as e:
                err_msg = str(e).lower()
                # If the model itself isn't found, try the next model immediately
                if "404" in err_msg or "not found" in err_msg:
                    continue 
                # If rate limited, try next key
                if "429" in err_msg or "quota" in err_msg:
                    break 
                else:
                    return f"❌ API Error: {str(e)}"

    return "❌ ALL MODELS/KEYS EXHAUSTED. Please check your API Dashboard."
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
