def scribe_translator(text_input):
    # A. LOAD THE LAW (rules.txt)
    # We keep this to ensure "Hard Swaps" for words you definitely want to control.
    rules_dict = {}
    if os.path.exists("rules.txt"):
        with open("rules.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    parts = line.split("=")
                    rules_dict[parts[0].strip().lower()] = parts[1].split("(")[0].strip()

    # B. PASS 1: THE HARD SWAP (Python-Driven)
    processed_text = text_input.lower()
    sorted_keys = sorted(rules_dict.keys(), key=len, reverse=True)
    
    for key in sorted_keys:
        pattern = re.compile(rf'\b{re.escape(key)}\b', re.IGNORECASE)
        processed_text = pattern.sub(rules_dict[key], processed_text)

    # C. THE MULTI-STEP INSTRUCTION
    # This tells the AI to translate anything that is still English into 1860s Afrikaans first.
    system_instruction = """
    ROLE: 19th-century Cape Muslim Scribe & Translator.
    
    TASK: 
    1. Look at the input. If any words are still in English, translate them into 1860s phonetic Cape Afrikaans (e.g., "you are" becomes "djie is", "cute" becomes "fyntjies" or "mooi").
    2. Once you have the 1860s Latin Afrikaans version, convert it into 1860s Arabic Script.

    STRICT ALPHABET MAPPING:
    - b=ب, p=پ, t=ت, s=س, dj=ج, tj=چ, h=ه, ch=خ, d=د, r=ر, sj=ش, f=ف, w=و, k=ك, g=گ, l=ل, m=م, n=ن, j=ي, ng=ڠ.
    - Vowels: a=ـَ, aa=ـَا, i/ie=ـِي, o/oo=ـُ, oe=ـُو, e(schwa)=ـِ.

    OUTPUT FORMAT:
    You must return TWO lines:
    Line 1: The Latin 1860s Afrikaans version.
    Line 2: The Arabic Script version.
    """

    # D. PASS 2: AI EXECUTION
    if "keys" not in st.secrets:
        return "❌ SETUP ERROR: Add 'keys' list to Streamlit Secrets."

    api_pool = st.secrets["keys"]

    for i, key in enumerate(api_pool):
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash', 
                system_instruction=system_instruction
            )
            
            # We ask the AI to be the final authority on the translation logic
            response = model.generate_content(
                f"Translate and convert: {processed_text}", 
                generation_config={"temperature": 0.1} # Slight temperature allows for better "guessing"
            )
            
            output = response.text.strip().split('\n')
            
            # Cleaning up empty lines if any
            output = [line for line in output if line.strip()]
            
            latin_ver = output[0].replace("Line 1:", "").strip()
            arabic_ver = output[1].replace("Line 2:", "").strip()

            return f"**1. Latin 1860s transcription:** {latin_ver}\n\n**2. Arabic script version:** {arabic_ver}"
            
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                if i < len(api_pool) - 1:
                    continue 
            return f"❌ System Error: {str(e)}"

    return "❌ All API paths failed."
