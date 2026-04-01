
import streamlit as st
import google.generativeai as genai
import os

# --- 1. UI SETUP ---
st.set_page_config(page_title="Master Scribe", page_icon="🕌")
st.title("🕌 1860s Arabic-Afrikaans Scribe")

# --- 2. KEY POOL ---
API_POOL = st.secrets.get("keys", [])
import streamlit as st
import google.generativeai as genai
import re
import os

# --- 1. UI SETUP ---
st.set_page_config(page_title="Master Scribe", page_icon="🕌")
st.title("🕌 1860s Arabic-Afrikaans Scribe")

# --- 2. KEY ROTATION (THE UNLIMITED FIX) ---
try:
    API_POOL = st.secrets["keys"]
except:
    st.error("⚠️ API Keys missing from Secrets Dashboard.")
    st.stop()

# --- 3. THE MASTER ENGINE (FORCED SHORT OUTPUT) ---
def scribe_translator(user_input):
    # Load your rules
    archive_rules = ""
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            archive_rules = f.read()

    for i, current_key in enumerate(API_POOL):
        try:
            genai.configure(api_key=current_key.strip())
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            
            # THE ULTIMATE "SHORT RESPONSE" PROMPT
            prompt = f"""
            ROLE: 19th-century Cape Muslim Scribe.
            TASK: Translate ONLY the INPUT below to 1860s Cape Afrikaans + Arabic Script.

            ### ALPHABET RULES:
            - Consonants: b=ب, p=پ, t=ت, s=ث/س/ص, dj=ج, tj=چ, h=ح/ه, ch/g=خ, d=د/ض, z=ذ/ز/ظ, r=ر, sj=ش, t=ط, g=غ, ng=ڠ, f=ف, w=ڤ/و, q=ق, k=ك, s/c=س, gh=گ, l=ل, m=م, n=ن, j=ي.
            - Vowels: a=ـَ, aa=ـَا, aai=ـَاي, ai=ـَي, ei/y=ـَِي, u/û=ـَِو, e=ـَِ, ê=ـَِـٰ, o=ـَُ, ie=ـِي, i=ـِ, î=ـِي, eeu/eu/uu=ـَِوي, ee=ـِي, oe=ـُ, ô=ـُو, oo=ـَُو, oei/ooi=ـُوي, ui=ـَُوي, e/è=ـَِي

            STRICT: Output ONLY two lines. No extra examples. No conversation.
            ARCHIVE RULES: {archive_rules}

            INPUT: {user_input}
            """
            
            # THE "ULTIMATE FIX" CONFIG: Stops AI from repeating itself
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 150, # Kills the "unlimited" text bug
                }
            )
            return response.text.strip()

        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                continue # Try next key
            return f"⚠️ Error: {e}"

    return "❌ All Project Quotas Exhausted."

# --- 4. UI ---
user_input = st.text_input("Enter sentence:")
if st.button("TRANSCRIBE"):
    if user_input:
        with st.spinner("Processing..."):
            result = scribe_translator(user_input)
            st.info(result)
# --- 3. UI LOGIC ---
user_input = st.text_input("Enter sentence:")
if st.button("TRANSCRIBE"):
    if user_input:
        with st.spinner("Applying Rules..."):
            st.info(scribe_translator(user_input))

