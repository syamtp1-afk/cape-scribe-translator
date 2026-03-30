import streamlit as st            
import google.generativeai as genai
import re
import os
import time
from google.api_core import exceptions

# 1. SETUP & AUTHENTICATION
# Add your keys here to multiply your 20-request limit
FREE_KEYS = [
    "AIzaSyDnI-xNlDOjTd7WKvlytbvjDJ5D6rxlnIk",  # Key 1 (Current)

    "AIzaSyB--5R7QKl4SqafBt_OZWRCc3ihIOhQiOE",                 # Key 2

    "AIzaSyAYoz5dz3BFAI0I5uLv_cpxPAi0hL8j-o8", 

    "AIzaSyCYoSfzTxYYuIDh1PYVw3uQXWLMX8BBK0Y", 

     "AIzaSyCwUz2zEcoxuXBWliPriSJ_pnIVY6JHygg"
]

def apply_linguistic_laws(text):
    text = text.lower()
    text = re.sub(r'ui', 'ei', text) 
    text = re.sub(r'\bge', 'ga', text) 
    text = re.sub(r'([aeiou])dd([aeiou])', r'\1rr\2', text) 
    return text

def scribe_translator(user_input):
    processed_text = apply_linguistic_laws(user_input)
    
    # Load rules safely
    archive_rules = "Follow 1860s Cape Muslim Scribe style."
    if os.path.exists("rules.txt"):
        try:
            with open("rules.txt", "r", encoding="utf-8") as f:
                archive_rules = f.read()
        except:
            pass

    # LOOP THROUGH KEYS FOR UNLIMITED-ISH FREE USE
    for current_key in FREE_KEYS:
        try:
            genai.configure(api_key=current_key)
            
            # Consistency Settings
            generation_config = {"temperature": 0, "top_p": 1}
            model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config)
            
            prompt = f"""

        ROLE: 19th-century Cape Muslim Scribe.

        TASK: Translate to 1860s Cape Afrikaans + Arabic Script.

        

         ### MANDATORY ALPHABET MAPPING:

       - Consonants: b=ب, p=پ, t=ت, s=ث/س/ص, dj=ج, tj=چ, h=ح/ه, ch/g=خ, d=د/ض, z=ذ/ز/ظ, r=ر, sj=ش, t=ط, g(soft)=غ, ng=ڠ, f=ف, w=ڤ/و, q/k=ق/ك, gh=گ, l=ل, m=م, n=ن, j=ي.

      - Vowels & Diphthongs:

     a=ـَ | aa=ـَا | aai=ـَاي | ai=ـَي | ei/y=ـَِي | u/û=ـَِو | e(schwa)=ـَِ | ê=ـَِـٰ | o=ـَُ | ie=ـِي | i=ـِ | î=ـِي(stroke) | eeu/eu/uu=ـَِوي | ee=ـِي | oe=ـُ | ô=ـُو | oo=ـَُو | oei/ooi=ـُوي | ui=ـَُوي | e/è=ـَِي

        

        STRICT: No greetings. No preamble. Output ONLY the numbered list.

        RULES: {archive_rules}

        

        OUTPUT FORMAT:

        1. Latin 1860s transcription: [Result]

        2. Arabic script version: [Result]

        

        INPUT: {processed_text}

        """ 
            
            response = model.generate_content(prompt)
            return response.text.strip() # This return is INSIDE the function (Correct)

        except exceptions.ResourceExhausted:
            # Current key is empty, the 'for' loop will try the next key
            continue 
        except Exception as e:
            return f"⚠️ System Error: {e}"

    # This return is also INSIDE the function, at the very end of the loop
    return "❌ ALL FREE KEYS EXHAUSTED. Create more keys or wait 24 hours."

# --- UI LOGIC (Outside the function) ---
st.set_page_config(page_title="Master Scribe", page_icon="🕌")
st.title("🕌 1860s Arabic-Afrikaans Scribe")

user_input = st.text_input("Enter sentence (English or Afrikaans):")

if st.button("TRANSCRIBE"):
    if user_input:
        with st.spinner("Consulting Manuscripts..."):
            result = scribe_translator(user_input)
            if "EXHAUSTED" in result:
                st.error(result)
            else:
                st.success(result)
    else:
        st.warning("Please enter text first.")