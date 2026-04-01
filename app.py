import streamlit as st
import google.generativeai as genai
import re
import os

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

def scribe_translator(text_input):
    # A. LOAD THE LAW (rules.txt) - The source of truth
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    # format: english_word = 1860s_latin_word
                    parts = line.split("=")
                    english_key = parts[0].strip().lower()
                    latin_val = parts[1].split("(")[0].strip()
                    rules_dict[english_key] = latin_val

    # B. DETERMINISTIC TRANSLATION (Python-Driven)
    # This prevents the AI from "hallucinating" or drifting.
    input_words = text_input.lower().split()
    translated_words = []
    
    for word in input_words:
        # Clean punctuation for the dictionary lookup
        clean_word = re.sub(r'[^\w\s]', '', word)
        # 100% Accuracy: If it's in your rules, use it. If not, keep original.
        translated_words.append(rules_dict.get(clean_word, word))
    
    final_latin_text = " ".join(translated_words)

    # C. THE SYSTEM INSTRUCTION (Script Accuracy Lock)
    system_instruction = """
    ROLE: 19th-century Cape Muslim Scribe.
    TASK: Convert the Latin text into EXACT 1860s Arabic Script.
    
    STRICT ALPHABET RULES:
    - Consonants: b=ب, p=پ, t=ت, s=س, dj=ج, tj=چ, h=ه, ch=خ, d=د, r=ر, sj=ش, f=ف, w=و, k=ك, g=گ, l=ل, m=م, n=ن, j=ي, ng=ڠ.
    - Vowels: a=ـَ, aa=ـَا, i/ie=ـِي, o/oo=ـُ, oe=ـُو, e(schwa)=ـِ.

    MANDATE: 
    1. Do NOT translate the words. 
    2. Do NOT change the spelling of the Latin provided.
    3. Simply map the characters of the provided input to the Arabic script.
    4. Output ONLY the Arabic Script.
    """

    # D. MULTI-KEY FAILOVER (Unlimited)
    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: Add 'keys' to Streamlit Secrets."

    api_pool = st.secrets["keys"]

    for i, key in enumerate(api_pool):
        try:
            genai.configure(api_key=key.strip())
            
            # Using the 2026 high-throughput model
            model = genai.GenerativeModel(
                model_name='gemini-3.1-flash-lite-preview',
                system_instruction=system_instruction
            )
            
            # Temperature 0.0 makes the AI a rigid robot (No drift)
            response = model.generate_content(
                f"LATIN INPUT: {final_latin_text}", 
                generation_config={"temperature": 0.0}
            )
            
            arabic_script = response.text.strip()
            return f"**1. Latin 1860s transcription:** {final_latin_text}\n\n**2. Arabic script version:** {arabic_script}"
            
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                if i < len(api_pool) - 1:
                    continue # Seamless jump to next key
            return f"❌ System Error: {str(e)}"

    return "❌ All API paths failed."

# --- 3. UI EXECUTION ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. you are soo cute", height=100)

if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Consultando Archivo..."):
            result = scribe_translator(user_input)
            st.info(result)
