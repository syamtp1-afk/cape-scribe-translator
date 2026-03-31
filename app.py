import streamlit as st
import google.generativeai as genai
import re
import os

# --- 1. UI SETUP ---
st.set_page_config(page_title="Master Scribe 1860", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

# --- 2. KEY POOL ---
API_POOL = st.secrets.get("keys", [])

def scribe_translator(user_input):
    # Load Vocabulary Laws from rules.txt
    archive_rules = "No additional vocabulary rules."
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            archive_rules = f.read()

    # THE BRAIN: System Instructions (Deterministic Mode)
    # This forces the AI to follow the mapping for EVERY word
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    TASK: Transcribe the INPUT into 1860s Cape Afrikaans and Arabic Script.
    
    ### MANDATORY VOCABULARY (PRIORITY #1):
    {archive_rules}
    
    ### MANDATORY ALPHABET LAWS (PRIORITY #2):
    - Consonants: b=ب, p=پ, t=ت, s=ث/س/ص, dj=ج, tj=چ, h=ح/ه, ch/g=خ, d=د/ض, z=ذ/ز/ظ, r=ر, sj=ش, t=ط, g=غ, ng=ڠ, f=ف, w=ڤ/و, q=ق, k=ك, s/c=س, gh=گ, l=ل, m=م, n=ن, j=ي.
    - Vowels & Diphthongs:
    a=ـَ | aa=ـَا | aai=ـَاي | ai=ـَي | ei/y=ـَِي | u/û=ـَِو | e(schwa)=ـَِ | ê=ـَِـٰ | o=ـَُ | ie=ـِي | i=ـِ | î=ـِي | eeu/eu/uu=ـَِوي | ee=ـِي | oe=ـُ | ô=ـُو | oo=ـَُو | oei/ooi=ـُوي | ui=ـَُوي | e/è=ـَِي

    EXECUTION PROTOCOL:
    1. Look at each word in the INPUT.
    2. If the word is in MANDATORY VOCABULARY, use the archive version.
    3. If the word is NOT in VOCABULARY, use the ALPHABET LAWS to frame the word phonetically.
    4. STRICTION: Output ONLY the two lines. No conversation.
    """

    for key in API_POOL:
        try:
            genai.configure(api_key=key.strip())
            # We use 'system_instruction' to lock the AI's behavior
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash-lite',
                system_instruction=system_instruction
            )
            
            # Temperature 0 = NO FOOLISHNESS. 100% Logic.
            response = model.generate_content(
                f"INPUT: {user_input}",
                generation_config={"temperature": 0}
            )
            return response.text.strip()
        except:
            continue
    return "❌ All Project Quotas Exhausted."

# --- 3. UI LOGIC ---
user_input = st.text_area("Input:", height=100)
if st.button("EXECUTE"):
    if user_input:
        with st.spinner("Scribe is working..."):
            st.info(scribe_translator(user_input))
