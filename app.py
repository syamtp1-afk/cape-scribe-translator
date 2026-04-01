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
                    # English Key = 1860s Latin Value
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # B. PASS 1: MANDATORY DICTIONARY SWAP (Python-Driven)
    # We sort by length to catch phrases like "what you want" before "what"
    processed_text = text_input.lower()
    sorted_keys = sorted(rules_dict.keys(), key=len, reverse=True)
    
    for key in sorted_keys:
        # Matches whole words only to prevent accidental swaps inside words
        pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[key], processed_text)

    # C. THE SYSTEM INSTRUCTION (The Script Guard)
    system_instruction = """
    ROLE: 19th-century Cape Muslim Scribe.
    TASK: Convert the provided 1860s Latin text into Arabic Script.
    
    STRICT ALPHABET:
    - Consonants: b=ب, p=پ, t=ت, s=س, dj=ج, tj=چ, h=ه, ch=خ, d=د, r=ر, sj=ش, f=ف, w=و, k=ك, g=گ, l=ل, m=م, n=ن, j=ي, ng=ڠ.
    - Vowels: a=ـَ, aa=ـَا, i/ie=ـِي, o/oo=ـُ, oe=ـُو, e(schwa)=ـِ.

    STRICT MANDATE: 
    1. The INPUT is already 1860s Latin Afrikaans. DO NOT TRANSLATE IT.
    2. Convert the letters of the input to the Arabic script EXACTLY.
    3. If the input is "wat djy wil", output "وَات جِي وِيل".
    4. Output ONLY the Arabic script.
    """

    # D. PASS 2: AI SCRIPT CONVERSION (Multi-Key Failover)
    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: Add 'keys' list to Streamlit Secrets."

    api_pool = st.secrets["keys"]

    for i, key in enumerate(api_pool):
        try:
            genai.configure(api_key=key.strip())
            
            # Using the 2026 Production Model
            model = genai.GenerativeModel(
                model_name='gemini-3.1-flash-lite-preview',
                system_instruction=system_instruction
            )
            
            # Temperature 0.0 = Absolute Accuracy
            response = model.generate_content(
                f"CONVERT THIS 1860s LATIN TO ARABIC SCRIPT: {processed_text}", 
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
user_input = st.text_area("Enter sentence:", placeholder="e.g. what you want", height=100)

if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Consultando Archivo..."):
            result = scribe_translator(user_input)
            st.info(result)
