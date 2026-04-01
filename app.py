import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
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

# --- 3. THE HARD-SWAP ENGINE (The "No-Drift" Fix) ---
def get_hard_dictionary():
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    modern = parts[0].strip().lower()
                    # Extracts archive word, removes anything in brackets (English meaning)
                    archive = parts[1].split("(")[0].strip()
                    rules_dict[modern] = archive
    return rules_dict

def scribe_translator(user_input):
    # STEP A: Physically swap words from rules.txt BEFORE the AI sees them
    # This prevents errors like "how are you" -> "هَاو اَر يُو"
    dictionary = get_hard_dictionary()
    processed_text = user_input.lower()
    for word in sorted(dictionary.keys(), key=len, reverse=True):
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        processed_text = pattern.sub(dictionary[word], processed_text)

    # STEP B: System Instructions (The "Phonetic Calculator" Mode)
    system_instruction = """
    ROLE: 19th-century Cape Muslim Scribe / Linguistic Researcher.
    TASK: Transcribe the INPUT sounds into 1860s Arabic Script.
    
    CRITICAL: 
    1. DO NOT translate meaning into Modern Arabic. 
    2. Transcribe ONLY the sounds of the words provided.
    3. Use: b=ب, p=پ, t=ت, s=ث, dj=ج, tj=چ, h=ح, ch=خ, d=د, r=ر, k=ك, l=ل, m=م, n=ن, w=و, j=ي.
    4. Vowels: a=ـَ, aa=ـَا, i/ie=ـِي, o/oo=ـُ, u=ـُ, e/è=ـَِي.

    OUTPUT FORMAT:
    1. Latin 1860s transcription: [Result]
    2. Arabic script version: [Result]
    """

    # STEP C: Key Rotation & Safety Handling
    for i, current_key in enumerate(API_POOL):
        try:
            genai.configure(api_key=current_key.strip())
            
            # BLOCK_NONE stops the 'Finish Reason 4' Copyright Error
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash-lite',
                system_instruction=system_instruction,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            
            response = model.generate_content(
                f"TRANSCRIBE: {processed_text}",
                generation_config={"temperature": 0} # Zero creativity = Pure Accuracy
            )

            # Check if AI blocked it despite settings
            if response.candidates[0].finish_reason == 4:
                return "⚠️ Safety Block: Segment flagged. Try rephrasing."

            return response.text.strip()

        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                if i < len(API_POOL) - 1: continue
                else: return "❌ ALL KEYS EXHAUSTED."
            return f"⚠️ System Error: {e}"

    return "❌ All Project Quotas Exhausted."

# --- 4. MAIN UI ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. read the quraan", height=100)

if st.button("EXECUTE"):
    if user_input:
        with st.spinner("Applying Archive Laws..."):
            result = scribe_translator(user_input)
            st.info(result)
    else:
        st.warning("Please enter text first.")

st.divider()
st.caption("Universal Scribe Engine v4.0 | Hard-Swap Logic Enabled")


