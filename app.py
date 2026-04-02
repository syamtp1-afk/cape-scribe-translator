import streamlit as st
import google.generativeai as genai
import re
import os
import random

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Cape Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Translator")

def scribe_translator(text_input):
    # --- STEP A: LOAD ARABIC-AFRIKAANS RULES ---
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                # Only parse lines with an equals sign for the dictionary
                if "=" in line and not line.startswith("#"):
                    parts = line.split("=")
                    rules_dict[parts[0].strip().lower()] = parts[1].strip()

    # --- STEP B: APPLY PHONOLOGICAL RULES ---
    # Manually applying the shifts found in the sources before AI processing
    processed_text = text_input.lower()
    processed_text = processed_text.replace("ui", "ei")  # Rule: ui > ei (uiwe > eiwe)
    processed_text = processed_text.replace("ge-", "ga-") # Rule: ge- > ga- (ge-maak > ga-maak)
    
    # Apply word-for-word mapping from rules_dict
    sorted_keys = sorted(rules_dict.keys(), key=len, reverse=True)
    for key in sorted_keys:
        pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[key], processed_text)

    # --- STEP C: SYSTEM INSTRUCTION (EXHAUSTIVE ORTHOGRAPHY) ---
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe using Arabic-Afrikaans.
    STRICT ORTHOGRAPHIC LAWS:
    1. Consonants: 'p' = پ, 'g' (great) = گ, 'g/gh' (guttural) = خ, 'ng' = نگ, 'tj' = چ, 'dj' = ج.
    2. Vowels: Short 'a' = fatha, Long 'aa' = fatha + alif, 'ie' = kasra + ya, 'oe' = damma + waw.
    3. Diphthongs: 'ei' = fatha + kasra + ya, 'au' = fatha + waw.
    4. No 'z' or 'v': Use 's' (س) and 'f' (ف) for 'v' sounds.
    5. 's' is 'sin' (س), but use 'sad' (ص) only for the word 'netsoes'.
    
    DICTIONARY PREFERENCE:
    {rules_dict}

    OUTPUT FORMAT:
    Latin: [Phonetic Cape Afrikaans]
    Arabic: [Arabic Script following Abu Bakr Effendi orthography]
    """

    # --- STEP D: API EXECUTION ---
    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: Add 'keys' list to Streamlit Secrets."

    api_pool = list(st.secrets["keys"])
    random.shuffle(api_pool)
    model_name = 'gemini-1.5-flash' 

    for key in api_pool:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
            response = model.generate_content(f"Translate to Cape Arabic-Afrikaans: {processed_text}")
            
            if response.text:
                return response.text
        except Exception as e:
            continue

    return "❌ Translation failed. Check your rules.txt formatting."

# --- UI EXECUTION ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. He is reading the prayer", height=100)
if st.button("EXECUTE SCRIBE"):
    if user_input:
        with st.spinner("📜 Writing in 19th-century Scribe..."):
            result = scribe_translator(user_input)
            st.info(result)
