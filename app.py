import streamlit as st
import google.generativeai as genai
import os

# --- 1. UI SETUP ---
st.set_page_config(page_title="Master Scribe", page_icon="🕌")
st.title("🕌 1860s Arabic-Afrikaans Scribe")

# --- 2. KEY POOL ---
API_POOL = st.secrets.get("keys", [])

def scribe_translator(user_input):
    # Load Rules from GitHub folder
    archive_rules = "No additional vocabulary rules."
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            archive_rules = f.read()

    # THE BRAIN: System Instructions force the AI to follow the rules
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    TASK: Translate input to 1860s Cape Afrikaans + Arabic Script.
    
    ### MANDATORY VOCABULARY:
    {archive_rules}
    
    ### ALPHABET LAWS:
    - Consonants: b=ب, p=پ, t=ت, s=ث/س/ص, dj=ج, tj=چ, h=ح/ه, ch/g=خ, d=د/ض, z=ذ/ز/ظ, r=ر, sj=ش, t=ط, g=غ, ng=ڠ, f=ف, w=ڤ/و, q=ق, k=ك, s/c=س, gh=گ, l=ل, m=م, n=ن, j=ي.
    - Vowels: a=ـَ, aa=ـَا, aai=ـَاي, ai=ـَي, ei/y=ـَِي, u/û=ـَِو, e=ـَِ, ê=ـَِـٰ, o=ـَُ, ie=ـِي, i=ـِ, î=ـِي, eeu/eu/uu=ـَِوي, ee=ـِي, oe=ـُ, ô=ـُو, oo=ـَُو, oei/ooi=ـُوي, ui=ـَُوي, e/è=ـَِي
### EXECUTION RULES:

    1. If a word is in the VOCABULARY list, use that word EXACTLY.

    2. Apply the ALPHABET LAWS to all other words.

    3. Output ONLY two lines:

       1. Latin 1860s transcription: [Result]

       2. Arabic script version: [Result]

    """
    for key in API_POOL:
        try:
            genai.configure(api_key=key.strip())
            # We "bake" the rules into the model identity here
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash-lite',
                system_instruction=system_instruction
            )
            
            # Temperature 0 = 100% Accuracy (No "creativity")
            response = model.generate_content(
                f"Translate: {user_input}",
                generation_config={"temperature": 0}
            )
            return response.text.strip()
        except:
            continue
    return "❌ All Project Quotas Exhausted."

# --- 3. UI LOGIC ---
user_input = st.text_input("Enter sentence:")
if st.button("TRANSCRIBE"):
    if user_input:
        with st.spinner("Applying Rules..."):
            st.info(scribe_translator(user_input))
