import streamlit as st
import google.generativeai as genai
import re
import os
import random

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

def scribe_translator(text_input):
    # --- STEP A: LOAD SUPREME RULES ---
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    # Expected format: English/Modern = 1860s/Nital (Phonetic)
                    parts = line.split("=")
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # --- STEP B: PRE-PROCESS TEXT (FORCING THE RULES) ---
    # We replace modern words with your specific Nital Nawayathi/Cape rules first
    processed_text = text_input.lower()
    sorted_keys = sorted(rules_dict.keys(), key=len, reverse=True)
    for key in sorted_keys:
        pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[key], processed_text)

    # --- STEP C: THE "IRONCLAD" SYSTEM INSTRUCTION ---
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe (Abu Bakr Effendi style).
    STRICT RULES:
    1. NEVER use modern Afrikaans or Dutch spelling.
    2. Use 'Abuljē' and 'M'ē:li' logic for Nital Nawayathi phonetics.
    3. ARABIC ORTHOGRAPHY:
       - 'f/v' sounds = ف
       - 'g' (guttural) = خ
       - 'oe' = و (Waw)
       - 'aa' = ا (Alif)
    
    REFERENCE DICTIONARY (PRIORITIZE THESE):
    {rules_dict}

    TASK: Convert the processed text into 1860s Cape Latin script AND Arabic Script.
    OUTPUT FORMAT:
    Line 1: [Latin Script]
    Line 2: [Arabic Script]
    """

    # --- STEP D: API EXECUTION ---
    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: Add 'keys' list to Streamlit Secrets."

    api_pool = list(st.secrets["keys"])
    random.shuffle(api_pool)
    
    # Use the stable 2026 model name
    model_name = 'gemini-1.5-flash' 

    for key in api_pool:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction
            )
            
            # We send the ALREADY rule-processed text to ensure the AI doesn't revert it
            response = model.generate_content(f"Scribe this exactly: {processed_text}")
            
            if response.text:
                lines = [l.strip() for l in response.text.strip().split('\n') if l.strip()]
                # Ensure we only get the transcription lines
                clean_lines = [line for line in lines if not line.startswith(('Line', 'Latin', 'Arabic'))]
                
                if len(clean_lines) >= 2:
                    return f"**1. Latin 1860s Transcription:**\n{clean_lines[0]}\n\n**2. Arabic Script Version:**\n{clean_lines[1]}"
                return response.text

        except Exception as e:
            if "404" in str(e):
                # Fallback for naming convention if 404 persists
                continue 
            st.warning(f"Attempt failed: {e}")
            continue

    return "❌ All attempts failed. Please verify your rules.txt format."

# --- 3. UI EXECUTION ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. how are you", height=100)
if st.button("EXECUTE SCRIBE"):
    if user_input:
        with st.spinner("📜 Applying Scribe Laws..."):
            result = scribe_translator(user_input)
            st.info(result)
