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

def scribe_translator(user_input):
    rules_dict = get_hard_dictionary()

    # 1. APPLY MANDATORY REPLACEMENTS (The Law)
    # We sort by length descending to ensure "school" is replaced before "schoolhouse"
    processed_text = user_input.lower()
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[word], processed_text)

    # 2. SYSTEM INSTRUCTION (Strict Enforcement)
    # Note: We tell the AI NOT to change the words, only to convert the script.
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    STRICT RULE: Use ONLY the provided Latin text. Do NOT modernize, do NOT fix grammar, and do NOT change words.
    
    TASK: 
    1. Output the provided Latin text exactly as given.
    2. Convert that Latin text into Arabic Script using the MAPPING below.

    ### MANDATORY ALPHABET MAPPING:
    - Consonants: b=ب, p=پ, t=ت, s=ث/س/ص, dj=ج, tj=چ, h=ح/ه, ch/g=خ, d=د/ض, z=ذ/ز/ظ, r=ر, sj=ش, t=ط, g(soft)=غ, ng=ڠ, f=ف, w=ڤ/و, q/k=ق/ك, gh=گ, l=ل, m=م, n=ن, j=ي.
    - Vowels: a=ـَ | aa=ـَا | aai=ـَاي | ai=ـَي | ei/y=ـَِي | u/û=ـَِو | e(schwa)=ـَِ | ê=ـَِـٰ | o=ـَُ | ie=ـِي | i=ـِ | î=ـِي(stroke) | eeu/eu/uu=ـَِوي | ee=ـِي | oe=ـُ | ô=ـُو | oo=ـَُو | oei/ooi=ـُوي | ui=ـَُوي | e/è=ـَِي

    ### ARCHIVE DICTIONARY USED FOR INPUT:
    {rules_dict}

    OUTPUT FORMAT:
    1. Latin 1860s transcription: [The processed text]
    2. Arabic script version: [The converted text]
    """

    for key in API_POOL:
        try:
            genai.configure(api_key=key.strip())
            # Updated to gemini-1.5-flash for stability (check availability of 2.5 in your region)
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
            
            # Temperature 0 ensures the AI doesn't "hallucinate" new spellings
            response = model.generate_content(
                f"CONVERT THIS SPECIFIC TEXT: {processed_text}", 
                generation_config={"temperature": 0}
            )
            return response.text.strip()
        except Exception as e:
            continue
    return "❌ Keys exhausted or API Error."

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
