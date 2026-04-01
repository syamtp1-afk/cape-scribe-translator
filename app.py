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
    # 1. Load Vocabulary from rules.txt into a "Hard Dictionary"
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    english_word = parts[0].strip().lower()
                    cape_word = parts[1].strip()
                    rules_dict[english_word] = cape_word

    # 2. FORCED SWAP: Python replaces words before the AI can "guess"
    # We sort by length (longest first) to avoid partial word replacements
    processed_text = user_input
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[word], processed_text)

    # 3. SYSTEM INSTRUCTION: The "Script Laws" for words NOT in the dictionary
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    TASK: Transcribe the INPUT into 1860s phonetic Cape Afrikaans and Arabic Script.
    
    ### THE LAW:
    1. Some words are ALREADY translated in the input. LEAVE THEM AS THEY ARE.
    2. For any modern words still present, use the ALPHABET MAPPING below.
    3. DO NOT translate meaning into Modern Arabic. Transcribe the SOUNDS only.
    
    ### ALPHABET MAPPING:
    - Consonants: b=ب, p=پ, t=ت, s=ث/س/ص, dj=ج, tj=چ, h=ح/ه, ch/g=خ, d=د/ض, z=ذ/ز/ظ, r=ر, sj=ش, t=ط, g=غ, ng=ڠ, f=ف, w=ڤ/و, q=ق, k=ك, s/c=س, gh=گ, l=ل, m=م, n=ن, j=ي.
    - Vowels: a=ـَ | aa=ـَا | aai=ـَاي | ai=ـَي | ei/y=ـَِي | u/û=ـَِو | e=ـَِ | ê=ـَِـٰ | o=ـَُ | ie=ـِي | i=ـِ | î=ـِي | eeu/eu/uu=ـَِوي | ee=ـِي | oe=ـُ | ô=ـُو | oo=ـَُو | oei/ooi=ـُوي | ui=ـَُوي | e/è=ـَِي

    OUTPUT FORMAT:
    1. Latin 1860s transcription: [Result]
    2. Arabic script version: [Result]
    """

    for key in API_POOL:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash-lite',
                system_instruction=system_instruction
            )
            
            # --- THE ACCURACY LOCK ---
            # Temperature 0 and high token limit for long, perfect translations
            response = model.generate_content(
                f"INPUT: {processed_text}",
                generation_config={
                    "temperature": 0,
                    "max_output_tokens": 1500 
                }
            )
            return response.text.strip()
        except Exception:
            continue
    return "❌ All Project Quotas Exhausted."
# --- 3. UI LOGIC ---
user_input = st.text_area("Input:", height=100)
if st.button("EXECUTE"):
    if user_input:
        with st.spinner("Scribe is working..."):
            st.info(scribe_translator(user_input))
