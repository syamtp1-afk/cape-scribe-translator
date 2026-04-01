import streamlit as st
import re
import os

# --- 1. UI SETUP ---
st.set_page_config(page_title="1860s Master Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Scribe")
st.markdown("### Zero-Quota Engine | 100% Offline Accuracy")

# --- 2. THE LOCAL PHONETIC ENGINE (The "No-AI" Fix) ---
def local_arabic_converter(text):
    """
    Converts 1860s Latin to Arabic Script using your MANDATORY mapping.
    This runs locally in Python. No API keys, no quota, no limits.
    """
    # Order matters: Longest phonetic strings must be replaced first (e.g., 'eeu' before 'ee')
    mapping = {
        # Diphthongs & Special Vowels
        'eeu': 'ـَِوي', 'oei': 'ُوي', 'ooi': 'ُوي', 'aai': 'ـَاي', 
        'eu': 'ـَِوي', 'uu': 'ـَِوي', 'ui': 'ـَُوي', 'ai': 'ـَي', 
        'ei': 'ـَِي', 'aa': 'ـَا', 'ee': 'ـِي', 'ie': 'ـِي', 
        'oe': 'ـُ', 'oo': 'ـَُو', 'ê': 'ـَِـٰ', 'ô': 'ـُو', 
        'î': 'ـِي', 'è': 'ـَِي', 'y': 'ـَِي',
        
        # Consonants (Complex)
        'dj': 'ج', 'tj': 'چ', 'sj': 'ش', 'ch': 'خ', 'gh': 'گ', 'ng': 'ڠ',
        
        # Consonants (Single)
        'b': 'ب', 'p': 'پ', 't': 'ت', 's': 'ث', 'h': 'ح', 'g': 'خ', 
        'd': 'د', 'z': 'ذ', 'r': 'ر', 'f': 'ف', 'w': 'و', 'q': 'ق', 
        'k': 'ك', 'l': 'ل', 'm': 'م', 'n': 'ن', 'j': 'ي',
        
        # Simple Vowels
        'a': 'ـَ', 'e': 'ـَِ', 'i': 'ـِ', 'o': 'ـَُ', 'u': 'ـَِو'
    }
    
    result = text.lower()
    for key, value in mapping.items():
        # Use word boundaries or simple replace? 
        # For script conversion, simple replace is more accurate for phonetics.
        result = result.replace(key, value)
    return result

def scribe_translator(text_input):
    # A. LOAD THE ARCHIVE (rules.txt)
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    # Modern = 1860s Latin
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # B. STEP 1: TRANSLATE (Modern -> 1860s Latin)
    # Using the Hard-Swap Dictionary
    latin_1860s = text_input.lower()
    for word in sorted(rules_dict.keys(), key=len, reverse=True):
        pattern = re.compile(rf'\b{re.escape(word)}\b', re.IGNORECASE)
        latin_1860s = pattern.sub(rules_dict[word], latin_1860s)

    # C. STEP 2: CONVERT (1860s Latin -> Arabic Script)
    # Using the Local Phonetic Engine
    arabic_script = local_arabic_converter(latin_1860s)

    # D. OUTPUT FORMAT (Exactly as requested)
    return f"""
1. Latin 1860s transcription: {latin_1860s}
2. Arabic script version: {arabic_script}
"""

# --- 3. UI EXECUTION ---
user_input = st.text_area("Enter sentence:", placeholder="e.g. how are you", height=100)

if st.button("EXECUTE"):
    if user_input:
        # No spinner needed - local execution is near-instant!
        result = scribe_translator(user_input)
        st.code(result.strip(), language=None)
    else:
        st.warning("Please enter text first.")

st.divider()
st.caption("Universal Scribe Engine v14.0 | Zero Quota | 100% Local Logic")
