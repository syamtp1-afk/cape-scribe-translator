import streamlit as st
import google.generativeai as genai
import re
import os

# --- 1. UI SETUP ---
st.set_page_config(page_title="Master Scribe 1860", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

# --- 2. KEY POOL ---
API_POOL = st.secrets.get("keys", [])

def get_hard_dictionary():
    """Reads rules.txt and creates a Python dictionary for forced swapping."""
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    # Splits 'Knowledge = Ilm' into key and value
                    parts = line.split("=")
                    english_word = parts[0].strip().lower()
                    cape_word = parts[1].strip()
                    rules_dict[english_word] = cape_word
    return rules_dict

def apply_hard_rules(text, rules_dict):
    """Physically replaces words from rules.txt before the AI sees them."""
    # We sort by length (longest first) so 'Knowledge' is replaced before 'Know'
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        text = pattern.sub(rules_dict[word], text)
    return text

def scribe_translator(user_input):
    # STEP 1: Forced Dictionary Swap (Python Power)
    dictionary = get_hard_dictionary()
    forced_text = apply_hard_rules(user_input, dictionary)

    # STEP 2: The AI Brain (Phonetic Framing for words NOT in dictionary)
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    TASK: The input text already has ARCHIVE words replaced. 
    Your ONLY job is to transcribe the REMAINING modern words into 1860s phonetics and Arabic Script.
    
    ### MANDATORY ALPHABET LAWS:
    - Consonants: b=ب, p=پ, t=ت, s=ث/س/ص, dj=ج, tj=چ, h=ح/ه, ch/g=خ, d=د/ض, z=ذ/ز/ظ, r=ر, sj=ش, t=ط, g=غ, ng=ڠ, f=ف, w=ڤ/و, q=ق, k=ك, s/c=س, gh=گ, l=ل, m=م, n=ن, j=ي.
    - Vowels: a=ـَ, aa=ـَا, aai=ـَاي, ai=ـَي, ei/y=ـَِي, u/û=ـَِو, e=ـَِ, ê=ـَِـٰ, o=ـَُ, ie=ـِي, i=ـِ, î=ـِي, eeu/eu/uu=ـَِوي, ee=ـِي, oe=ـُ, ô=ـُو, oo=ـَُو, oei/ooi=ـُوي, ui=ـَُوي, e/è=ـَِي

    STRICT: Output ONLY the two numbered lines. No conversation.
    """

    for key in API_POOL:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash-lite',
                system_instruction=system_instruction
            )
            
            # Temp 0 ensures the AI follows the alphabet laws for non-dictionary words
            response = model.generate_content(
                f"TRANSCRIBE THIS: {forced_text}",
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
