import streamlit as st
import google.generativeai as genai
import re
import os
import time

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

# --- 2. THE ENGINE (The Ultimate Fail-Proof Version) ---
def scribe_translator(text_input):
    # A. LOAD DICTIONARY (rules.txt)
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # B. HARD-SWAP (Zero-Inaccuracy Python Layer)
    processed_text = text_input.lower()
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[word], processed_text)

    # C. STRICT SYSTEM INSTRUCTION
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    STRICT COMMAND: The input is ALREADY 1860s Latin. DO NOT TRANSLATE.
    ONLY CONVERT TO ARABIC SCRIPT USING THIS MAP:
    b=ب | p=پ | t=ت | s=ث/س/ص | dj=ج | tj=چ | h=ح/ه | ch/g=خ | d=د/ض | z=ذ/ز/ظ | r=ر | sj=ش | t=ط | g=غ | ng=ڠ | f=ف | w=و | q/k=ق | gh=گ | l=ل | m=م | n=ن | j=ي
    Vowels: a=ـَ | aa=ـَا | ie=ـِي | oe=ـُ | oo=ـَُو | e=ـَِ | ee=ـِي
    
    OUTPUT:
    1. Latin 1860s transcription: {processed_text}
    2. Arabic script version: [Converted Text]
    """

    # D. MULTI-KEY FAILOVER WITH DIAGNOSTICS
    try:
        api_keys = st.secrets["keys"]
    except Exception:
        return "❌ ERROR: 'keys' not found in Streamlit Secrets. Check your secrets.toml file."

    for i, key in enumerate(api_keys):
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
            
            # Use Temperature 0 and add a 1-second safety pause between attempts if needed
            response = model.generate_content(
                f"CONVERT: {processed_text}", 
                generation_config={"temperature": 0}
            )
            return response.text.strip()
            
        except Exception as e:
            error_msg = str(e)
            # If it's a rate limit (429), wait 2 seconds and try ONE more time before moving to next key
            if "429" in error_msg:
                time.sleep(2)
                try:
                    response = model.generate_content(f"CONVERT: {processed_text}", generation_config={"temperature": 0})
                    return response.text.strip()
                except:
                    st.warning(f"⚠️ Key {i+1} rate-limited. Trying next...")
                    continue
            elif "400" in error_msg:
                st.error(f"🚫 Key {i+1} is INVALID. Check for typos.")
                continue
            else:
                st.warning(f"⚠️ Key {i+1} failed: {error_msg[:50]}...")
                continue

    return "❌ CRITICAL: All keys exhausted. Please wait 60 seconds and try again."

# --- 3. UI EXECUTION (No NameError) ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. excuse me", height=100)

if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Pulling from Archives..."):
            final_output = scribe_translator(user_input)
            st.info(final_output)
    else:
        st.warning("Please enter text.")

st.divider()
st.caption("Universal Scribe Engine v5.5 | Fix: 429 Retry & Key Diagnostics")
