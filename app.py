import streamlit as st
import google.generativeai as genai
import re
import os

# --- 1. SETTINGS & UI ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")
st.markdown("### Official Universal Accurate Translator")

# --- 2. THE ENGINE ---
def scribe_translator(text_input):
    # A. LOAD THE LAW (rules.txt)
    # This ensures "excuse me" ALWAYS becomes "Ekskuus my"
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    # Key: Modern | Value: 1860s Archive
                    modern = parts[0].strip().lower()
                    archive = parts[1].split("(")[0].strip()
                    rules_dict[modern] = archive

    # B. THE HARD INTERCEPT (Python Level)
    # We replace words BEFORE the AI sees them. This is the "Zero Drift" fix.
    processed_text = text_input.lower()
    # Sort by length to catch phrases before single words
    sorted_keys = sorted(rules_dict.keys(), key=len, reverse=True)
    for word in sorted_keys:
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[word], processed_text)

    # C. THE SCRIPT PROTOCOL (Alphabet Map)
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    STRICT COMMAND: The input provided is ALREADY the correct 1860s Latin translation. 
    DO NOT translate it. DO NOT fix it. DO NOT add modern Arabic.
    
    TASK: 
    1. Output 'Latin 1860s transcription: [The input]'
    2. Output 'Arabic script version: [The input converted to Arabic characters]'

    MANDATORY ALPHABET MAPPING:
    - b=ب | p=پ | t=ت | s=ث/س/ص | dj=ج | tj=چ | h=ح/ه | ch/g=خ | d=د/ض | z=ذ/ز/ظ | r=ر | sj=ش | t=ط | g(soft)=غ | ng=ڠ | f=ف | w=ڤ/و | q/k=ق/ك | gh=گ | l=ل | m=م | n=ن | j=ي.
    - Vowels: a=ـَ | aa=ـَا | aai=ـَاي | ai=ـَي | ei/y=ـَِي | u/û=ـَِو | e(schwa)=ـَِ | ê=ـَِـٰ | o=ـَُ | ie=ـِي | i=ـِ | î=ـِي(stroke) | eeu/eu/uu=ـَِوي | ee=ـِي | oe=ـُ | ô=ـُو | oo=ـَُو | oei/ooi=ـُوي | ui=ـَُوي | e/è=ـَِي

    ALPHABET EXAMPLE: 'Ekskuus my' -> 'اِکْسُوس مِي'
    """

    # D. API FAILOVER
    try:
        api_pool = st.secrets["keys"]
    except:
        return "⚠️ SETUP ERROR: Keys missing in Secrets."

    for key in api_pool:
        try:
            genai.configure(api_key=key.strip())
            # 1.5-Flash is used for stability and strict adherence to system instructions
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
            
            # Temperature 0 = Mathematical consistency (No creativity)
            response = model.generate_content(
                f"CONVERT THIS LATIN TO ARABIC SCRIPT: {processed_text}", 
                generation_config={"temperature": 0}
            )
            return response.text.strip()
        except:
            continue
    
    return "❌ All API paths exhausted."

# --- 3. UI EXECUTION (Fixed NameError Scope) ---
# Define variable BEFORE the button
user_input = st.text_area("Enter sentence:", placeholder="e.g. excuse me", height=100)

if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Consulting Archive Laws..."):
            result = scribe_translator(user_input)
            st.info(result)
    else:
        st.warning("Please enter text first.")

st.divider()
st.caption("Universal Scribe Engine v5.0 | Hard-Swap Logic | 100% adherence to rules.txt")
