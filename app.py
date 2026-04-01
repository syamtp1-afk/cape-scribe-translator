import streamlit as st
import google.generativeai as genai
import re
import os

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

def scribe_translator(text_input):
    # A. LOAD THE LAW (rules.txt)
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    # Key = English, Value = 1860s Afrikaans
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # B. PASS 1: MANDATORY DICTIONARY SWAP (100% Accuracy)
    # We sort keys by length (longest first) to catch "how are you" before "how"
    processed_text = text_input.lower()
    sorted_keys = sorted(rules_dict.keys(), key=len, reverse=True)
    
    for key in sorted_keys:
        pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[key], processed_text)

    # C. THE SYSTEM INSTRUCTION (Script Lock)
    system_instruction = """
    ROLE: 19th-century Cape Muslim Scribe.
    TASK: Convert the input text into 1860s Arabic Script.
    
    STRICT ALPHABET:
    - b=ب, p=پ, t=ت, s=س, dj=ج, tj=چ, h=ه, ch=خ, d=د, r=ر, sj=ش, f=ف, w=و, k=ك, g=گ, l=ل, m=م, n=ن, j=ي, ng=ڠ.
    - Vowels: a=ـَ, aa=ـَا, i/ie=ـِي, o/oo=ـُ, oe=ـُو, e(schwa)=ـِ.

    MANDATE: 
    1. Do NOT translate. The input is already in 1860s Latin.
    2. Map the letters of the input to the Arabic script EXACTLY.
    3. Output ONLY the Arabic script. No English.
    """

    # D. PASS 2: AI SCRIPT CONVERSION (Unlimited/High Throughput)
    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: Add 'keys' list to Streamlit Secrets."

    api_pool = st.secrets["keys"]

    for i, key in enumerate(api_pool):
        try:
            genai.configure(api_key=key.strip())
            
            # 2026 Production Model: Gemini 3.1 Flash-Lite
            model = genai.GenerativeModel(
                model_name='gemini-3.1-flash-lite-preview',
                system_instruction=system_instruction
            )
            
            # Temperature 0.0 = Robot accuracy
            response = model.generate_content(
                f"CONVERT TO ARABIC SCRIPT: {processed_text}", 
                generation_config={"temperature": 0.0}
            )
            
            arabic_script = response.text.strip()
            return f"**1. Latin 1860s transcription:** {processed_text}\n\n**2. Arabic script version:** {arabic_script}"
            
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                if i < len(api_pool) - 1:
                    continue 
            return f"❌ System Error: {str(e)}"

    return "❌ All API paths failed."

# --- 3. UI EXECUTION ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. how are you", height=100)

if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Consulting Archive Laws..."):
            result = scribe_translator(user_input)
            st.info(result)
