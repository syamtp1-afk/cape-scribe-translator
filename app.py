import streamlit as st
import google.generativeai as genai
import re
import os

# --- 1. SETTINGS ---
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
                    modern = parts[0].strip().lower()
                    archive = parts[1].split("(")[0].strip()
                    rules_dict[modern] = archive

    # B. HARD-SWAP (Python Pre-Processor)
    processed_text = text_input.lower()
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[word], processed_text)

    # C. EMBED RULES INTO THE AI BRAIN
    # We send the top rules directly to the AI so it learns the "style" instantly
    dictionary_sample = str(list(rules_dict.items())[:20]) # First 20 rules

    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    
    CRITICAL INSTRUCTION: 
    - The input text has ALREADY been partially translated using the Archive Dictionary.
    - If a word looks like 1860s Afrikaans, DO NOT change it.
    - For 'how are you', the ONLY correct 1860s translation is 'Hoe faa nog'.
    - DO NOT use 'Hoe is djy'. That is modern/wrong for this scribe.
    
    DICTIONARY LAW: {dictionary_sample}

    ARABIC SCRIPT MAP:
    b=ب | p=پ | t=ت | s=ث/س | dj=ج | tj=چ | h=ح | ch/g=خ | d=د | r=ر | sj=ش | f=ف | w=و | k=ك | g=گ | l=ل | m=م | n=ن | j=ي
    Vowels: a=ـَ | aa=ـَا | ie=ـِي | oe=ـُ | oo=ـَُو | e=ـَِ | ee=ـِي | o=ـَُ

    OUTPUT FORMAT:
    Latin 1860s transcription: [The Corrected Latin]
    Arabic script version: [The Script Version]
    """

    # D. API EXECUTION
    try:
        api_keys = st.secrets["keys"]
        genai.configure(api_key=api_keys[0].strip())
        
        # Use Temperature 0.0 to kill ALL AI creativity
        model = genai.GenerativeModel("gemini-3-flash-preview", system_instruction=system_instruction)
        
        response = model.generate_content(
            f"TRANSLATE '{text_input}' TO 1860s LATIN AND ARABIC. CURRENT PROCESSED STATE: {processed_text}", 
            generation_config={"temperature": 0.0} 
        )
        
        return response.text.strip()
    except Exception as e:
        return f"❌ System Error: {str(e)}"

# --- 3. UI ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. how are you", height=100)

if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Consulting Archive..."):
            result = scribe_translator(user_input)
            st.info(result)
    else:
        st.warning("Please enter text.")

st.divider()
st.caption("Universal Scribe Engine v10.0 | Zero-Drift Logic | Temperature 0.0")
