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
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # B. PASS 1: THE HARD SWAP
    processed_text = text_input.lower()
    sorted_keys = sorted(rules_dict.keys(), key=len, reverse=True)
    for key in sorted_keys:
        pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[key], processed_text)

    # C. THE MULTI-STEP SYSTEM INSTRUCTION
    system_instruction = """
    ROLE: 19th-century Cape Muslim Scribe & Translator.
    TASK: 
    1. Translate English words to 1860s Cape Afrikaans (Latin script).
    2. Convert that Afrikaans into 1860s Arabic Script using the mapping below.
    
    ALPHABET MAPPING:
    - b=ب, p=پ, t=ت, s=س, dj=ج, tj=چ, h=ه, ch=خ, d=د, r=ر, sj=ش, f=ف, w=و, k=ك, g=گ, l=ل, m=م, n=ن, j=ي, ng=ڠ.
    - Vowels: a=ـَ, aa=ـَا, i/ie=ـِي, o/oo=ـُ, oe=ـُو, e(schwa)=ـِ.

    OUTPUT RULE:
    Return EXACTLY two lines. 
    Line 1: [Latin Version]
    Line 2: [Arabic Script Version]
    """

    # D. API EXECUTION
    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: Add 'keys' list to Streamlit Secrets."

    api_pool = st.secrets["keys"]
    
    # FIX: Use the latest stable production model alias
    # 'gemini-1.5-flash' is often deprecated in favor of 'gemini-2.0-flash' or 'gemini-pro'
    # For 2026, we use the current production standard:
    SELECTED_MODEL = 'gemini-2.0-flash' 

    for i, key in enumerate(api_pool):
        try:
            genai.configure(api_key=key.strip())
            
            # Initialize model with the new stable name
            model = genai.GenerativeModel(
                model_name=SELECTED_MODEL, 
                system_instruction=system_instruction
            )
            
            response = model.generate_content(
                f"Input to process: {processed_text}", 
                generation_config={"temperature": 0.2}
            )
            
            # Split and clean output
            lines = [l.strip() for l in response.text.strip().split('\n') if l.strip()]
            
            if len(lines) >= 2:
                # Remove labels if the AI included them
                latin_out = lines[0].replace("Line 1:", "").replace("[", "").replace("]", "").strip()
                arabic_out = lines[1].replace("Line 2:", "").replace("[", "").replace("]", "").strip()
                return f"**1. Latin 1860s transcription:** {latin_out}\n\n**2. Arabic script version:** {arabic_out}"
            else:
                return f"**Result:**\n{response.text}"
                
        except Exception as e:
            # If the specific model is still 404, we try a fallback model
            if "404" in str(e) and SELECTED_MODEL != 'gemini-pro':
                SELECTED_MODEL = 'gemini-pro'
                continue
            
            if i < len(api_pool) - 1:
                continue 
            return f"❌ System Error: {str(e)}"
            
    return "❌ All API paths failed."

# --- 3. UI EXECUTION ---
# Wrapping in a try block to prevent the "Blank Screen of Death"
try:
    user_input = st.text_area("Enter sentence:", placeholder="e.g. you are cute", height=100)

    if st.button("EXECUTE"):
        if user_input:
            with st.spinner("📜 Consulting Archive Laws..."):
                result = scribe_translator(user_input)
                st.info(result)
        else:
            st.warning("Please enter text first.")
except Exception as e:
    st.error(f"Critical App Error: {e}")
