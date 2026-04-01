import streamlit as st
import google.generativeai as genai
import re
import os
import random

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

def scribe_translator(text_input):
    # A. RE-WRITING THE PHONETIC ENGINE
    # The 1860s dialect used 'v/f' for 'w' sounds and 'jille' for 'u/hulle'
    processed_text = text_input.lower()
    
    # B. 1860s LINGUISTIC RULES (Force the dialect)
    # We replace modern Afrikaans with the 1869 'Bayan al-Din' dialect
    dialect_map = {
        "hoe gaan dit met u": "hoe faar nog",
        "hulle": "he:li", # Per Achmat Davids 1894 research
        "gaan": "faar",
        "met": "mie",
        "u": "jille"
    }
    
    for k, v in dialect_map.items():
        processed_text = processed_text.replace(k, v)

    # C. SYSTEM INSTRUCTION (Phonetic Orthography)
    # This forces the Arabic script to match 1860s Cape Malay standards
    system_instruction = """
    ROLE: Abu Bakr Effendi (1860s Cape Muslim Scholar).
    LANGUAGE: Cape Arabic-Afrikaans (Kitaab-Hollandsch).
    
    TRANSCRIPTION RULES:
    1. 'f' or 'v' sound = ف
    2. 'g' (guttural) = خ (kha) or غ (ghayn)
    3. 'oo' / 'aa' = ا or ـَا
    4. 'ee' = ي or ـِي
    5. 'oe' = و or ـُو
    
    TASK: Translate the input into 1860s Cape Dialect, then provide the Arabic Script.
    EXAMPLE: 'How are you' -> 
    Line 1: hoe faar nog
    Line 2: هُو فَار نُوغ
    """

    # API Configuration
    if "keys" not in st.secrets: return "❌ Add keys to secrets."
    api_key = random.choice(st.secrets["keys"])
    genai.configure(api_key=api_key.strip())

    try:
        # Use Gemini 1.5 Flash or Pro (ensure 'models/' prefix is NOT there if it failed before)
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
        
        response = model.generate_content(f"Scribe this: {processed_text}")
        
        if response.text:
            # Cleaning up the response to ensure two clean lines
            output = response.text.strip().split('\n')
            latin = output[0].replace("Line 1:", "").strip()
            arabic = output[-1].replace("Line 2:", "").strip()
            
            return f"**1. Latin 1860s Transcription:**\n{latin}\n\n**2. Arabic Script Version:**\n{arabic}"
    except Exception as e:
        return f"❌ Error: {e}"

# --- UI EXECUTION ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. how are you", height=100)
if st.button("EXECUTE"):
    if user_input:
        with st.spinner("📜 Dipping the quill..."):
            st.info(scribe_translator(user_input))
