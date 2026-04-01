import streamlit as st
import google.generativeai as genai
import re
import os

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")
st.markdown("### Official Universal Accurate Translator")

# --- 2. GET KEYS SAFELY ---
try:
    API_POOL = st.secrets["keys"]
except Exception:
    st.error("⚠️ SETUP ERROR: API Keys not found in Streamlit Secrets.")
    st.stop()

# --- 3. THE HARD-SWAP ENGINE ---
def get_hard_dictionary():
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    # Key is modern, Value is the 1860s transcription
                    modern = parts[0].strip().lower()
                    archive = parts[1].split("(")[0].strip()
                    rules_dict[modern] = archive
    return rules_dict

import streamlit as st
import google.generativeai as genai
import re
import os
import time

# --- 1. THE RECOVERY LOGIC (Ultimate Fix for API Errors) ---
def call_gemini_with_retry(model, prompt, retries=2):
    """Attempts to call the API with a small delay if it hits a rate limit."""
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt, generation_config={"temperature": 0})
            return response.text.strip()
        except Exception as e:
            if "429" in str(e):  # Rate limit error
                time.sleep(2)  # Wait 2 seconds and try again
                continue
            raise e
    return None

def scribe_translator(user_input):
    # 1. LOAD RULES
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # 2. HARD-SWAP (The Python Shield)
    processed_text = user_input.lower()
    # Sort by length descending to catch longer phrases first
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[word], processed_text)

    # 3. SYSTEM INSTRUCTION (The Script Lock)
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    STRICT COMMAND: Your input is ALREADY translated into 1860s Latin transcription. 
    DO NOT change the spelling of the input. 
    
    TASK:
    1. Provide the 'Latin 1860s transcription' exactly as the input.
    2. Provide the 'Arabic script version' by mapping that Latin text using:
    b=ب, p=پ, t=ت, s=ث, dj=ج, tj=چ, h=ح, ch=خ, d=د, r=ر, sj=ش, f=ف, w=و, k=ك, g=گ, l=ل, m=م, n=ن, j=ي
    Vowels: a=ـَ, aa=ـَا, ie=ـِي, oe=ـُ, oo=ـَُو, e=ـَِ

    INPUT: {processed_text}
    """

    # 4. MULTI-KEY FAILOVER LOOP
    for key in API_POOL:
        try:
            genai.configure(api_key=key.strip())
            # Use 1.5-Flash for highest stability and quota
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
            
            result = call_gemini_with_retry(model, f"CONVERT TO ARABIC SCRIPT: {processed_text}")
            if result:
                return result
        except Exception as e:
            # Silently try next key if this one is dead/invalid
            continue

    return "❌ CRITICAL ERROR: All API paths blocked. Check internet or API quota."

# --- UI EXECUTION ---
if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Consultng the Archives..."):
            result = scribe_translator(user_input)
            st.markdown(f"### Result\n{result}")

# --- 4. MAIN UI ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. excuse me", height=100)

if st.button("EXECUTE"):
    if user_input:
        with st.spinner("Applying Archive Laws..."):
            result = scribe_translator(user_input)
            st.info(result)
    else:
        st.warning("Please enter text first.")

st.divider()
st.caption("Universal Scribe Engine v4.0 | Hard-Swap Logic Enabled")
