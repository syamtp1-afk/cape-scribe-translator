import streamlit as st
import google.generativeai as genai
import re
import os
import random
import time

# --- UI ---
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


# --- HARD BASE MAP (VERY IMPORTANT) ---
BASE_MAP = {
    "hello": "salaam",
    "hi": "salaam",
    "prayer": "salaat",
    "fast": "poewasa",
    "fasting": "poewasa",
    "reading": "lees",
    "read": "lees",
    "after": "ba'd",
    "before": "qabl",
    "god": "allaah",
    "allah": "allaah",
    "book": "kitaab",
    "water": "maa",
    "eat": "eet",
    "drink": "drink",
    "go": "gaan"
}


# --- LAYER 1: RULE ENGINE ---
def apply_base_rules(text, rules_dict):
    text = text.lower()

    # base map
    for k, v in BASE_MAP.items():
        text = re.sub(rf'\b{k}\b', v, text)

    # phonology
    text = text.replace("ui", "ei")
    text = text.replace("ge-", "ga-")
    text = re.sub(r'([dt])\1', 'rr', text)

    # external rules.txt
    for key in sorted(rules_dict.keys(), key=len, reverse=True):
        text = re.sub(rf'\b{re.escape(key)}\b', rules_dict[key], text)

    return text


# --- LAYER 3: POST FIX ENGINE (CRITICAL) ---
def force_post_fix(text):
    text = text.lower()

    # remove English leakage
    fixes = {
        "hello": "salaam",
        "hi": "salaam",
        "the": "die",
        "and": "wa",
        "of": "van",
        "to": "naar"
    }

    for k, v in fixes.items():
        text = re.sub(rf'\b{k}\b', v, text)

    return text


# --- FALLBACK (NO AI) ---
def fallback_output(processed):
    return f"""1. Latin 1860s transcription:
{processed}

2. Arabic script version:
[AI unavailable — add more API keys]
"""


# --- MAIN TRANSLATOR ---
def scribe_translator(user_input):
    rules_dict, archive_rules = load_rules()

    # --- LAYER 1 ---
    processed = apply_base_rules(user_input, rules_dict)

    # --- LAYER 2 (AI STYLE ENGINE) ---
    system_instruction = f"""
You are a 19th-century Cape Muslim scribe.

IMPORTANT:
- Input is already partially converted Cape-Afrikaans
- You MUST transform into manuscript Arabic-Afrikaans
- Add Arabic/Persian vocabulary (40–50%)
- Use Cape Muslim rhythm and phrasing
- NEVER output English
- NEVER repeat input unchanged

STRICT OUTPUT FORMAT:
1. Latin 1860s transcription: ...
2. Arabic script version: ...

RULES:
{archive_rules}

INPUT:
{processed}
"""

    # --- API CHECK ---
    if "keys" not in st.secrets:
        return fallback_output(processed)

    keys = list(st.secrets["keys"])
    random.shuffle(keys)

    # --- API LOOP ---
    for key in keys:
        try:
            genai.configure(api_key=key.strip())

            model = genai.GenerativeModel(
                model_name="gemini-1.5-pro"  # 🔥 upgraded model
            )

            response = model.generate_content(system_instruction)

            if response and response.text:
                fixed = force_post_fix(response.text)
                return fixed

        except Exception:
            time.sleep(1)
            continue

    # --- FINAL FALLBACK ---
    return fallback_output(processed)


# --- UI ---
user_input = st.text_area(
    "Enter sentence:",
    placeholder="e.g. He is reading the prayer after the fast",
    height=120
)

if st.button("EXECUTE SCRIBE"):
    if user_input.strip():
        with st.spinner("📜 Writing Manuscript..."):
            result = scribe_translator(user_input)
            st.success(result)
