#!/usr/bin/env python3
"""
AGENT 03: VOICE SCRIPT WRITER
Generates scripts in your personal voice style using Groq API
"""

import os
import sys
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def analyze_voice_patterns():
    """Analyze my_scripts.txt to extract voice patterns"""
    try:
        with open('my_scripts.txt', 'r', encoding='utf-8') as f:
            scripts = f.read()
    except FileNotFoundError:
        print("❌ my_scripts.txt not found")
        sys.exit(1)
    
    return """
VOICE ANALYSIS FROM my_scripts.txt:

1. VOCABULARY:
   - Uses Hinglish mix naturally (अगर, ऐसी, etc.)
   - Direct, no-fluff language
   - Business terms: "conversion", "funnel", "automation", "system"
   - Currency in ₹ (rupees)
   - Strong action words: "STOP", "NO", "gone", "waste"

2. SENTENCE STRUCTURE:
   - Very short, punchy lines (3-7 words average)
   - Uses "→" for flow/progression
   - Lists with "No X / No Y / No Z" pattern
   - Rhetorical questions followed by answers

3. OPENING STYLE:
   - Starts with problem/pain point
   - Uses "अगर" (if) to create relatability
   - Direct commands: "STOP", "Don't"
   - Shocking statements: "90% fail", "Your competitor is..."

4. STRUCTURE PATTERN:
   - Problem statement (2-3 lines)
   - Why it matters (2-3 lines)
   - Solution/offer (1-2 lines)
   - Always ends with clear CTA

5. CTA STYLE:
   - Always uses DM or Comment trigger
   - Format: "DM '[KEYWORD]' — [what they get]"
   - Or: "Comment '[KEYWORD]' if [condition]"
   - Keywords in ALL CAPS

6. LANGUAGE MIX:
   - 80% English, 20% Hindi
   - Hindi used for emotional connection
   - English for technical/business terms
   - Never translates Hindi words

7. ENERGY:
   - Authoritative but not arrogant
   - Urgent without being pushy
   - Confident, direct, no hedging
   - Uses ellipsis (…) for dramatic pause
"""

def generate_script(topic):
    """Generate script using Groq API"""
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ GROQ_API_KEY not found in .env file")
        sys.exit(1)
    
    client = Groq(api_key=api_key)
    
    voice_patterns = analyze_voice_patterns()
    
    system_prompt = f"""You are a script writer who writes EXACTLY in this creator's voice:

{voice_patterns}

CRITICAL RULES:
- Write in the EXACT style shown above
- Mix Hindi and English naturally (Hinglish)
- Keep sentences SHORT and PUNCHY
- NO generic openings like "Today I will" or "In this video"
- NO formal language
- Use "→" for progression
- End with DM/Comment CTA in the exact format shown

STRUCTURE (DO NOT include hook):
[BEAT 2] — Main value/point (2-3 sentences)
[BEAT 3] — Example or proof (2-3 sentences)  
[BEAT 4] — CTA (comment trigger, match style)

Topic: {topic}

Write ONLY beats 2-4. NO HOOK. Match the voice EXACTLY."""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Write a script about: {topic}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        script = completion.choices[0].message.content
        return script
        
    except Exception as e:
        print(f"❌ Groq API error: {str(e)}")
        sys.exit(1)

def main():
    print("=" * 60)
    print("AGENT 03: VOICE SCRIPT WRITER")
    print("=" * 60)
    
    # Get topic from command line or use default
    if len(sys.argv) > 1:
        topic = ' '.join(sys.argv[1:])
    else:
        topic = "AI automation for businesses"
        print(f"📌 Using default topic: {topic}")
    
    print(f"\n🎯 Topic: {topic}")
    print("\n⏳ Generating script...")
    
    script = generate_script(topic)
    
    # Save to file
    with open('voice_script_output.txt', 'w', encoding='utf-8') as f:
        f.write(f"TOPIC: {topic}\n\n")
        f.write(script)
    
    # Print result
    print("\n" + "=" * 60)
    print("GENERATED SCRIPT:")
    print("=" * 60)
    print(script)
    print("=" * 60)
    
    print(f"\n✅ Saved to voice_script_output.txt")

if __name__ == "__main__":
    main()
