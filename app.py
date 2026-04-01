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
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # B. HARD-SWAP (Check Dictionary First)
    processed_text = text_input.lower()
    dictionary_matches = []
    
    # Identify words already translated by rules.txt to tell the AI "Don't touch these"
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        if word in processed_text:
            pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
            processed_text = pattern.sub(rules_dict[word], processed_text)
            dictionary_matches.append(rules_dict[word])

    # C. THE SMART-GUESS SYSTEM INSTRUCTION
    # We provide the AI with the dialect rules so its "guesses" are accurate.
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    TASK: Translate input to 1860s Cape Afrikaans AND convert to Arabic Script.
    
    ### THE LAW:
    1. If a word is already in 1860s Latin (like {dictionary_matches}), DO NOT CHANGE IT.
    2. If a word is in Modern English/Afrikaans, translate it to 1860s Cape Dialect.
       - Example: 'thank you' -> 'danki'
       - Example: 'what' -> 'wat'
       - Example: 'read' -> 'rieti'
    
    ### ARABIC SCRIPT MAP:
    Consonants: b=ب, p=پ, t=ت, s=ث, dj=ج, tj=چ, h=ح, ch=خ, d=د, r=ر, sj=ش, f=ف, w=و, k=ك, g=گ, l=ل, m=م, n=ن, j=ي
    Vowels: a=ـَ, aa=ـَا, ie=ـِي, oe=ـُ, oo=ـَُو, e=ـَِ, ee=ـِي

    OUTPUT FORMAT:
    Latin 1860s transcription: [Result]
    Arabic script version: [Result]
    """

    # D. API EXECUTION
    try:
        api_keys = st.secrets["keys"]
        # Use Gemini 3 Flash for the best 2026 reasoning
        model_name = "gemini-3-flash-preview" 
        
        genai.configure(api_key=api_keys[0].strip())
        model = genai.GenerativeModel(model_name, system_instruction=system_instruction)
        
        # We use a slightly higher temperature (0.2) to allow "guessing" only when dictionary fails
        response = model.generate_content(
            f"TRANSLATE AND CONVERT: {processed_text}", 
            generation_config={"temperature": 0.2}
        )
        
        return response.text.strip()
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- 3. MAIN UI ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. thank you", height=100)

if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Consulting Archive & Scribe Wisdom..."):
            result = scribe_translator(user_input)
            st.info(result)
    else:
        st.warning("Please enter text.")

st.divider()
st.caption("Universal Scribe Engine v9.0 | Hybrid Dictionary-AI Logic")
