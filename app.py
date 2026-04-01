import streamlit as st
import google.generativeai as genai
import re
import os
import time

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

def scribe_translator(text_input):
    # A. LOAD THE LAW (rules.txt)
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    # Key = English, Value = 1860s Latin
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # B. DETERMINISTIC LATIN TRANSLATION (100% Rule Adherence)
    # We do this in Python, NOT AI, to ensure 0% drift.
    words = text_input.lower().split()
    latin_results = []
    for word in words:
        # Clean punctuation for lookup
        clean_word = re.sub(r'[^\w\s]', '', word)
        # Use rule if exists, otherwise keep original (or mark as unknown)
        latin_results.append(rules_dict.get(clean_word, word))
    
    final_latin = " ".join(latin_results)

    # C. THE SYSTEM INSTRUCTION (The "Zero-Drift" Script Guard)
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    TASK: Convert the provided 1860s Latin Afrikaans into EXACT Arabic Script.
    
    STRICT ALPHABET:
    - b=ب, p=پ, t=ت, s=س, dj=ج, tj=چ, h=ه, ch=خ, d=د, r=ر, sj=ش, f=ف, w=و, k=ك, g=گ, l=ل, m=م, n=ن, j=ي, ng=ڠ.
    - Vowels: a=ـَ, aa=ـَا, i/ie=ـِي, o/oo=ـُ, oe=ـُو, e(schwa)=ـِ.

    RULE: 
    1. Do NOT translate. Do NOT add words. Do NOT change the Latin provided.
    2. Transliterate the INPUT string letter-for-letter based on the mapping.
    3. Output ONLY the Arabic Script. No preamble.
    """

    # D. MULTI-KEY FAILOVER (Unlimited Logic)
    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: 'keys' list missing in Streamlit Secrets."

    api_pool = st.secrets["keys"]

    for i, key in enumerate(api_pool):
        try:
            genai.configure(api_key=key.strip())
            # Using Gemini 3.1 Flash for high RPM/Unlimited feel
            model = genai.GenerativeModel(
                model_name='gemini-3.1-flash-lite-preview',
                system_instruction=system_instruction
            )
            
            # We pass the ALREADY TRANSLATED Latin to the AI for script conversion only
            response = model.generate_content(
                f"CONVERT TO ARABIC SCRIPT: {final_latin}", 
                generation_config={"temperature": 0.0} # 0.0 for absolute determinism
            )
            
            arabic_script = response.text.strip()
            
            return f"**1. Latin 1860s transcription:** {final_latin}\n\n**2. Arabic script version:** {arabic_script}"
            
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                if i < len(api_pool) - 1:
                    continue # Try next key
            return f"❌ System Error: {str(e)}"

    return "❌ All API paths failed."

# --- 3. UI EXECUTION ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. you are soo cute", height=100)

if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Consulting Archive Laws..."):
            result = scribe_translator(user_input)
            st.info(result)
