import streamlit as st
import google.generativeai as genai
import re
import os
import random
import time

# --- UI SETUP ---
st.set_page_config(page_title="1860s Cape Arabic-Afrikaans Scribe", page_icon="🕌")
st.title("🕌 1860s Cape Arabic-Afrikaans Translator")

# --- LOAD RULES ---
def load_rules():
    rules_dict = {}
    raw_text = ""

    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            raw_text = f.read()

            matches = re.findall(r'^([\w\s]+)\s*=\s*([\w\s\-]+)', raw_text, re.MULTILINE)
            for key, val in matches:
                rules_dict[key.strip().lower()] = val.strip()

    return rules_dict, raw_text


# --- FALLBACK TRANSLATOR (NO AI) ---
def fallback_translate(text, rules_dict):
    text = text.lower()

    for key in sorted(rules_dict.keys(), key=len, reverse=True):
        text = re.sub(rf'\b{re.escape(key)}\b', rules_dict[key], text)

    return f"""1. Latin 1860s transcription:
{text}

2. Arabic script version:
[AI unavailable — add more API keys]
"""


# --- MAIN TRANSLATOR ---
def scribe_translator(text_input):
    rules_dict, archive_rules = load_rules()

    # --- STEP A: PREPROCESS ---
    processed = text_input.lower()

    processed = processed.replace("ui", "ei")
    processed = processed.replace("ge-", "ga-")
    processed = re.sub(r'([dt])\1', 'rr', processed)

    for key in sorted(rules_dict.keys(), key=len, reverse=True):
        processed = re.sub(rf'\b{re.escape(key)}\b', rules_dict[key], processed)

    # --- STEP B: PROMPT ---
    system_instruction = f"""
ROLE: 19th-century Cape Muslim Scribe.

TASK: Convert into historic Cape Arabic-Afrikaans.

STRICT RULES:
- No English
- No explanation
- No greetings
- Output ONLY 2 numbered lines

STYLE:
- 40–50% Arabic/Persian vocabulary
- Cape Muslim oral rhythm
- Manuscript tone

RULE SOURCE:
{archive_rules}

FORMAT:
1. Latin 1860s transcription: ...
2. Arabic script version: ...

INPUT:
{processed}
"""

    # --- STEP C: API HANDLING ---
    if "keys" not in st.secrets:
        return fallback_translate(processed, rules_dict)

    api_pool = list(st.secrets["keys"])
    random.shuffle(api_pool)

    for key in api_pool:
        try:
            genai.configure(api_key=key.strip())

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_instruction
            )

            response = model.generate_content(processed)

            if response and response.text:
                return response.text

        except Exception as e:
            time.sleep(1)  # cooldown
            continue

    # --- FINAL FALLBACK ---
    return fallback_translate(processed, rules_dict)


# --- UI EXECUTION ---
user_input = st.text_area(
    "Enter sentence:",
    placeholder="e.g. He is reading the prayer after the fast",
    height=100
)

if st.button("EXECUTE SCRIBE"):
    if user_input:
        with st.spinner("📜 Applying Scribe Laws..."):
            result = scribe_translator(user_input)
            st.success(result)
