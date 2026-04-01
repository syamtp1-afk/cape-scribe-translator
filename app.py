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
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # B. HARD-SWAP (Python Pre-Processor)
    processed_text = text_input.lower()
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[word], processed_text)

    # C. THE SYSTEM INSTRUCTION
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    TASK: Translate to 1860s Cape Afrikaans + Arabic Script.

    ### MANDATORY ALPHABET MAPPING:
    - Consonants: b=ب, p=پ, t=ت, s=ث/س/ص, dj=ج, tj=چ, h=ح/ه, ch/g=خ, d=د/ض, z=ذ/ز/ظ, r=ر, sj=ش, t=ط, g(soft)=غ, ng=ڠ, f=ف, w=ڤ/و, q/k=ق/ك, gh=گ, l=ل, m=م, n=ن, j=ي.
    - Vowels: a=ـَ | aa=ـَا | aai=ـَاي | ai=ـَي | ei/y=ـَِي | u/û=ـَِو | e=ـَِ | ie=ـِي | o=ـَُ | oe=ـُ | ô=ـُو | oo=ـَُو | ui=ـَُوي
    
    STRICT: No greetings. Output ONLY the numbered list.
    DICTIONARY RULES: {list(rules_dict.items())}

    OUTPUT FORMAT:
    1. Latin 1860s transcription: [Result]
    2. Arabic script version: [Result]
    """

    # D. MULTI-KEY FAILOVER
    try:
        api_pool = st.secrets["keys"]
    except:
        return "❌ SETUP ERROR: API Keys missing in Secrets."

    for i, key in enumerate(api_pool):
        try:
            genai.configure(api_key=key.strip())
            
            # FIXED MODEL NAME: gemini-1.5-flash-latest
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash-latest',
                system_instruction=system_instruction
            )
            
            response = model.generate_content(
                f"INPUT: {processed_text}", 
                generation_config={"temperature": 0.1, "top_p": 1}
            )
            return response.text.strip()
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg: # Rate Limit
                if i < len(api_pool) - 1:
                    time.sleep(1) # Small pause before trying next key
                    continue
                else:
                    return "❌ ALL KEYS EXHAUSTED: Please wait 60 seconds."
            return f"❌ System Error: {error_msg}"

    return "❌ All API paths failed."

# --- 3. UI EXECUTION ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. hoe gaat dit", height=100)

if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Consulting Archive Laws..."):
            result = scribe_translator(user_input)
            st.info(result)
    else:
        st.warning("Please enter text first.")
