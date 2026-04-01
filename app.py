

# --- 3. THE MASTER ENGINE (FORCED SHORT OUTPUT) ---
import streamlit as st
import google.generativeai as genai
import re
import os

# --- 1. UI SETUP (Keeps the site from being blank) ---
st.set_page_config(page_title="Master Scribe", page_icon="🕌")
st.title("🕌 1860s Arabic-Afrikaans Scribe")
st.markdown("### Official Universal Translator")

# --- 2. GET KEYS SAFELY FROM SECRETS ---
try:
    # This pulls your pool of keys from the Streamlit Secrets dashboard
    # Expected format in Secrets: keys = ["AIza...", "AIza...", "AIza..."]
    API_POOL = st.secrets["keys"]
except Exception:
    st.error("⚠️ SETUP ERROR: API Keys not found. Please add them to the Streamlit Secrets dashboard.")
    st.stop()

# --- 3. LINGUISTIC PROCESSING ---
def apply_linguistic_laws(text):
    """Phonetic pre-processing for authentic 1860s Cape style."""
    text = text.lower()
    text = re.sub(r'ui', 'ei', text) 
    text = re.sub(r'\bge', 'ga', text) 
    text = re.sub(r'([aeiou])dd([aeiou])', r'\1rr\2', text) 
    return text

# --- 4. THE ULTIMATE TRANSLATOR ENGINE ---
def scribe_translator(user_input):
    processed_text = apply_linguistic_laws(user_input)
    
    # Load dictionary rules from rules.txt if it exists
    archive_rules = "No additional dictionary rules."
    if os.path.exists("rules.txt"):
        try:
            with open("rules.txt", "r", encoding="utf-8") as f:
                archive_rules = f.read()
        except:
            pass

    # THE PROJECT ROTATION ENGINE: Multiplying your free quota
    for i, current_key in enumerate(API_POOL):
        try:
            genai.configure(api_key=current_key)
            
            # Using 'gemini-2.5-flash-lite' for the highest daily free limits
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            
            # THE ULTIMATE PROMPT (Directing the AI's Brain)
            prompt = f"""
ROLE: 19th-century Cape Muslim Scribe.
TASK: Translate to 1860s Cape Afrikaans + Arabic Script.

### MANDATORY ALPHABET MAPPING:
- Consonants: b=ب, p=پ, t=ت, s=ث/س/ص, dj=ج, tj=چ, h=ح/ه, ch/g=خ, d=د/ض, z=ذ/ز/ظ, r=ر, sj=ش, t=ط, g(soft)=غ, ng=ڠ, f=ف, w=ڤ/و, q=ق, k=ك, s/c=س, gh=گ, l=ل, m=م, n=ن, j=ي.
- Vowels & Diphthongs:
a=ـَ | aa=ـَا | aai=ـَاي | ai=ـَي | ei/y=ـَِي | u/û=ـَِو | e(schwa)=ـَِ | ê=ـَِـٰ | o=ـَُ | ie=ـِي | i=ـِ | î=ـِي(stroke) | eeu/eu/uu=ـَِوي | ee=ـِي | oe=ـُ | ô=ـُو | oo=ـَُو | oei/ooi=ـُوي | ui=ـَُوي | e/è=ـَِي

STRICT: No greetings. No preamble. Output ONLY the numbered list.
DICTIONARY RULES: {archive_rules}

OUTPUT FORMAT:
1. Latin 1860s transcription: [Result]
2. Arabic script version: [Result]

INPUT: {processed_text}
"""
            
            response = model.generate_content(
                prompt, 
                generation_config={"temperature": 0} # Zero creativity = Maximum accuracy
            )
            return response.text.strip()

        except Exception as e:
            # Check if this project is empty (Quota Error)
            if "429" in str(e) or "quota" in str(e).lower():
                if i < len(API_POOL) - 1:
                    continue # Silently move to the next project key
                else:
                    return "❌ ALL PROJECT QUOTAS EXHAUSTED. Please wait for the daily reset or add more keys."
            return f"⚠️ System Error: {e}"

    return "❌ All Project Quotas Exhausted for today."

# --- 5. MAIN APP LOGIC ---
user_input = st.text_input("Enter sentence (English or Afrikaans):", placeholder="e.g. Give me knowledge")

if st.button("TRANSCRIBE"):
    if user_input:
        with st.spinner("Consulting Manuscripts..."):
            result = scribe_translator(user_input)
            st.info(result)
    else:
        st.warning("Please enter text first.")

st.divider()
st.caption("Powered by Key-Rotation Engine v3.0 | 1860s Archive Edition")
# --- 3. UI LOGIC ---
user_input = st.text_input("Enter sentence:")
if st.button("TRANSCRIBE"):
    if user_input:
        with st.spinner("Applying Rules..."):
            st.info(scribe_translator(user_input))

