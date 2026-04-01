import streamlit as st
import google.generativeai as genai
import re
import os

# --- 1. SETTINGS & UI ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

# --- 2. THE ENGINE ---
def scribe_translator(text_input):
    # A. LOAD THE ARCHIVE (rules.txt)
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    # Key: Modern English/Afrikaans | Value: 1860s Cape Afrikaans
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # B. THE HARD TRANSLATION (Python Level)
    processed_text = text_input.lower()
    found_match = False
    
    # Sort keys to match phrases before single words
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        if word in processed_text:
            pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
            processed_text = pattern.sub(rules_dict[word], processed_text)
            found_match = True

    # C. FAILSAFE: If word is not in rules.txt, don't let AI guess the dialect
    if not found_match:
        return "⚠️ WORD NOT IN ARCHIVE: Please add this word/phrase to rules.txt to ensure 100% accuracy."

    # D. SCRIPT LOGIC (The Alphabet Map)
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    STRICT TASK: You are a script converter. Convert the provided 1860s Latin text into 1860s Arabic Script.
    DO NOT translate. DO NOT change spellings. 
    
    ALPHABET:
    b=ب, p=پ, t=ت, s=ث, dj=ج, tj=چ, h=ح, ch=خ, d=د, r=ر, sj=ش, f=ف, w=و, k=ك, g=گ, l=ل, m=م, n=ن, j=ي
    Vowels: a=ـَ, aa=ـَا, ie=ـِي, oe=ـُ, oo=ـَُو, e=ـَِ, ee=ـِي
    """

    # E. API EXECUTION
    try:
        api_keys = st.secrets["keys"]
        # Use the latest 2026 model names
        model_name = "gemini-3-flash-preview" 
        
        genai.configure(api_key=api_keys[0].strip()) # Using first available key
        model = genai.GenerativeModel(model_name, system_instruction=system_instruction)
        
        response = model.generate_content(f"CONVERT TO ARABIC SCRIPT: {processed_text}", generation_config={"temperature": 0})
        
        return f"**Latin 1860s transcription:** {processed_text}\n\n**Arabic script version:** {response.text.strip()}"
    
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# --- 3. MAIN UI ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. how are you", height=100)

if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Consulting Archive..."):
            result = scribe_translator(user_input)
            if "⚠️" in result:
                st.warning(result)
            else:
                st.info(result)
    else:
        st.warning("Please enter text.")

st.divider()
st.caption("Universal Scribe Engine v8.0 | Strict Dictionary Enforcement")
