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
    # 1. Load your rules from rules.txt into a 'Hard Swap' dictionary
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    # Standardizing to lowercase for matching
                    modern = parts[0].strip().lower() 
                    # Extracting the 1860s word before any notes in brackets
                    archive = parts[1].split("(")[0].strip() 
                    rules_dict[modern] = archive

    # 2. THE FORCE: Python replaces words before the AI even sees them
    # This prevents the AI from guessing "Read = رید"
    processed_text = user_input.lower()
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[word], processed_text)

    # 3. THE AI BRAIN: Only used for Arabic Script and remaining phonetics
    system_instruction = """
    ROLE: 1860s Cape Muslim Scribe.
    TASK: Transcribe the input into Arabic Script using these EXACT LAWS:
    - b=ب, p=پ, t=ت, s=ث, dj=ج, tj=چ, h=ح, ch=خ, d=د, r=ر, k=ك, l=ل, m=م, n=ن, w=و, j=ي.
    - Vowels: a=ـَ, aa=ـَا, i/ie=ـِي, o/oo=ـُ, u=ـُ.
    STRICT: Use the Arabic mapping for the words provided. Output ONLY two lines.
    """

    for key in API_POOL:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash-lite',
                system_instruction=system_instruction
            )
            # Temperature 0 is mandatory for 100% accuracy
            response = model.generate_content(
                f"TEXT: {processed_text}",
                generation_config={"temperature": 0}
            )
            return response.text.strip()
        except:
            continue
    return "❌ System Busy. Try again."

# --- 3. UI LOGIC ---
user_input = st.text_area("Input:", height=100)
if st.button("EXECUTE"):
    if user_input:
        with st.spinner("Scribe is working..."):
            st.info(scribe_translator(user_input))
