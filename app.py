import streamlit as st
import google.generativeai as genai
import os

# --- 1. UI SETUP ---
st.set_page_config(page_title="Master Scribe 1860", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")

# --- 2. KEY POOL ---
API_POOL = st.secrets.get("keys", [])

def scribe_translator(user_input):
    # Load Vocabulary Laws from rules.txt
    archive_rules = ""
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            archive_rules = f.read()

    # THE BRAIN: Few-Shot Prompting for 100% Accuracy
    system_instruction = f"""
    ROLE: 19th-century Cape Muslim Scribe.
    TASK: Transcribe the INPUT text into 1860s phonetic Cape Afrikaans and Arabic Script.
    
    ### MASTER VOCABULARY (PRIORITY #1):
    {archive_rules}
    
    ### MANDATORY ALPHABET LAWS:
    - Consonants: b=ب, p=پ, t=ت, s=ث/س/ص, dj=ج, tj=چ, h=ح/ه, ch/g=خ, d=د/ض, z=ذ/ز/ظ, r=ر, sj=ش, t=ط, g=غ, ng=ڠ, f=ف, w=ڤ/و, q=ق, k=ك, s/c=س, gh=گ, l=ل, m=م, n=ن, j=ي.
    - Vowels: a=ـَ, aa=ـَا, aai=ـَاي, ai=ـَي, ei/y=ـَِي, u/û=ـَِو, e=ـَِ, ê=ـَِـٰ, o=ـَُ, ie=ـِي, i=ـِ, î=ـِي, eeu/eu/uu=ـَِوي, ee=ـِي, oe=ـُ, ô=ـُو, oo=ـَُو, oei/ooi=ـُوي, ui=ـَُوي, e/è=ـَِي

    ### PERFECT EXECUTION EXAMPLE:
    Input: "Die grafiek van relatiewe snelhied"
    1. Latin 1860s transcription: Die grafiek van relatiewe snelhied
    2. Arabic script version: دِي غْرَافِيِك ڤَان رَلَاتِيِوِي سْنَلْهِيِد

    STRICT RULES: 
    1. NEVER skip a word from the input.
    2. NEVER change the meaning of a word.
    3. Use the Arabic mapping for EVERY single letter.
    4. Output ONLY the two numbered lines.
    """

    for key in API_POOL:
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash-lite',
                system_instruction=system_instruction
            )
            
            # Use 'User' role to clearly separate the input
            response = model.generate_content(
                f"TEXT TO TRANSCRIBE: {user_input}",
                generation_config={
                    "temperature": 0, 
                    "top_p": 0.1,
                    "max_output_tokens": 500
                }
            )
            return response.text.strip()
        except:
            continue
    return "❌ All Project Quotas Exhausted."

# --- 3. UI LOGIC ---
user_input = st.text_area("Enter text to transcribe:", height=150)
if st.button("EXECUTE SCRIBE"):
    if user_input:
        with st.spinner("Writing..."):
            st.info(scribe_translator(user_input))
