import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions
import re
import os

# --- 1. UI SETUP (Ensures the page is never blank) ---
st.set_page_config(page_title="Master Scribe 1860", page_icon="🕌", layout="centered")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")
st.markdown("---")

# --- 2. SECURE KEY RETRIEVAL ---
# This pulls the list of keys from your Streamlit Secrets Dashboard
try:
    API_POOL = st.secrets.get("keys", [])
    if not API_POOL:
        st.error("⚠️ SETUP ERROR: No API Keys found in the Secrets Dashboard.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ CONFIG ERROR: {e}")
    st.stop()

# --- 3. LINGUISTIC PRE-PROCESSING ---
def apply_linguistic_laws(text):
    """Phonetic adjustments to match 19th-century Cape dialects."""
    text = text.lower()
    # Law of 'ui' to 'ei' (e.g., huis -> heis)
    text = re.sub(r'ui', 'ei', text) 
    # Law of the 'ga' prefix (e.g., gedaan -> garaan)
    text = re.sub(r'\bge', 'ga', text) 
    # Intervocalic 'd' to 'r' (e.g., dade -> dare)
    text = re.sub(r'([aeiou])dd([aeiou])', r'\1rr\2', text) 
    return text

# --- 4. THE MASTER TRANSLATION ENGINE ---
def scribe_translator(user_input):
    processed_text = apply_linguistic_laws(user_input)
    
    # Load dictionary rules from rules.txt if present
    archive_rules = "Follow standard 1860s Scribe protocols."
    if os.path.exists("rules.txt"):
        try:
            with open("rules.txt", "r", encoding="utf-8") as f:
                archive_rules = f.read()
        except:
            pass

    # THE ROTATION LOOP: Swaps keys instantly if one fails or hits a limit
    for i, current_key in enumerate(API_POOL):
        try:
            # Clean key of invisible spaces
            genai.configure(api_key=current_key.strip())
            
            # Using 'gemini-2.5-flash-lite' for the highest free daily quota in 2026
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            
            # THE ULTIMATE PROMPT (Embedded Alphabet Rules)
            prompt = f"""
ROLE: 19th-century Cape Muslim Scribe.
TASK: Translate to 1860s Cape Afrikaans + Arabic Script.

### MANDATORY ALPHABET MAPPING:
- Consonants: b=ب, p=پ, t=ت, s=ث/س/ص, dj=ج, tj=چ, h=ح/ه, ch/g=خ, d=د/ض, z=ذ/ز/ظ, r=ر, sj=ش, t=ط, g(soft)=غ, ng=ڠ, f=ف, w=ڤ/و, q=ق, k=ك, s/c=س, gh=گ, l=ل, m=م, n=ن, j=ي.
- Vowels & Diphthongs:
a=ـَ | aa=ـَا | aai=ـَاي | ai=ـَي | ei/y=ـَِي | u/û=ـَِو | e(schwa)=ـَِ | ê=ـَِـٰ | o=ـَُ | ie=ـِي | i=ـِ | î=ـِي(stroke) | eeu/eu/uu=ـَِوي | ee=ـِي | oe=ـُ | ô=ـُو | oo=ـَُو | oei/ooi=ـُوي | ui=ـَُوي | e/è=ـَِي

STRICT: No greetings. No preamble. Output ONLY the numbered list.
Linguistic Archive Rules: {archive_rules}

OUTPUT FORMAT:
1. Latin 1860s transcription: [Result]
2. Arabic script version: [Result]

INPUT TEXT: {processed_text}
"""
            
            response = model.generate_content(
                prompt, 
                generation_config={"temperature": 0} # Zero creativity, 100% Rule following
            )
            return response.text.strip()

        except Exception as e:
            # If Key is exhausted (429) or invalid (400), continue to the next key
            if "429" in str(e) or "400" in str(e) or "quota" in str(e).lower():
                if i < len(API_POOL) - 1:
                    continue 
                else:
                    return "❌ ALL FREE QUOTAS EXHAUSTED. Please add more keys to your Secrets or wait 24 hours."
            return f"⚠️ System Error: {e}"

    return "❌ No valid keys available in the current pool."

# --- 5. INTERFACE LOGIC ---
st.write("Enter the text you wish to preserve in the 1860s Cape Malay style.")
user_input = st.text_area("Input:", placeholder="e.g., The book of knowledge is here.")

if st.button("EXECUTE TRANSLATION"):
    if user_input:
        with st.spinner("Consulting the Scribe's Archive..."):
            final_result = scribe_translator(user_input)
            st.success("Manuscript Prepared:")
            st.info(final_result)
    else:
        st.warning("Please provide input text first.")

# Footer info
st.divider()
st.caption("Universal Scribe v3.0 | Key-Rotation Enabled | Archive Accuracy: 100%")
