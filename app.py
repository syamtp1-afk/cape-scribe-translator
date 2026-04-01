import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
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

# --- 3. THE HARD-SWAP ENGINE (The "No-Drift" Fix) ---
def get_hard_dictionary():
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    modern = parts[0].strip().lower()
                    # Extracts archive word, removes anything in brackets (English meaning)
                    archive = parts[1].split("(")[0].strip()
                    rules_dict[modern] = archive
    return rules_dict
def scribe_translator(user_input):
    # 1. LOAD THE MASTER DICTIONARY (Law)
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    modern = parts[0].strip().lower()
                    archive = parts[1].split("(")[0].strip() # Clean meanings
                    rules_dict[modern] = archive

    # 2. THE HARD INTERCEPTOR (Python Power)
    # This physically deletes 'how' and writes 'hoe' before the AI sees it
    processed_text = user_input.lower()
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[word], processed_text)

    # 3. THE "SCRIBE-ONLY" SYSTEM INSTRUCTION
    system_instruction = """
    ROLE: 19th-century Cape Muslim Scribe.
    TASK: Translate to 1860s Cape Afrikaans + Arabic Script.

        

         ### MANDATORY ALPHABET MAPPING:

       - Consonants: b=ب, p=پ, t=ت, s=ث/س/ص, dj=ج, tj=چ, h=ح/ه, ch/g=خ, d=د/ض, z=ذ/ز/ظ, r=ر, sj=ش, t=ط, g(soft)=غ, ng=ڠ, f=ف, w=ڤ/و, q/k=ق/ك, gh=گ, l=ل, m=م, n=ن, j=ي.

      - Vowels & Diphthongs:

     a=ـَ | aa=ـَا | aai=ـَاي | ai=ـَي | ei/y=ـَِي | u/û=ـَِو | e(schwa)=ـَِ | ê=ـَِـٰ | o=ـَُ | ie=ـِي | i=ـِ | î=ـِي(stroke) | eeu/eu/uu=ـَِوي | ee=ـِي | oe=ـُ | ô=ـُو | oo=ـَُو | oei/ooi=ـُوي | ui=ـَُوي | e/è=ـَِي
    COMMAND: Output ONLY 1. Latin 1860s 2. Arabic Script. NO MODERN ARABIC.
    RULES: {archive_rules}

        

        OUTPUT FORMAT:

        1. Latin 1860s transcription: [Result]

        2. Arabic script version: [Result]

        

        INPUT: {processed_text}

        """ 
            

    for key in API_POOL:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel('gemini-2.5-flash-lite', system_instruction=system_instruction)
            # Temperature 0: The Absolute Accuracy Lock
            response = model.generate_content(f"TEXT: {processed_text}", generation_config={"temperature": 0})
            return response.text.strip()
        except:
            continue
    return "❌ Keys exhausted."
# --- 4. MAIN UI ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. read the quraan", height=100)

if st.button("EXECUTE"):
    if user_input:
        with st.spinner("Applying Archive Laws..."):
            result = scribe_translator(user_input)
            st.info(result)
    else:
        st.warning("Please enter text first.")

st.divider()
st.caption("Universal Scribe Engine v4.0 | Hard-Swap Logic Enabled")


