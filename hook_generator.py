#!/usr/bin/env python3
"""
AGENT 04: HOOK GENERATOR
Generates 5 different hook variations using proven viral patterns
"""

import os
import sys
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def read_script_and_topic():
    """Read the generated script and topic"""
    try:
        with open('voice_script_output.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract topic
        topic_line = [line for line in content.split('\n') if line.startswith('TOPIC:')]
        topic = topic_line[0].replace('TOPIC:', '').strip() if topic_line else "Unknown"
        
        return topic, content
    except FileNotFoundError:
        print("❌ voice_script_output.txt not found. Run voice_writer.py first.")
        sys.exit(1)

def analyze_hook_style():
    """Analyze hook patterns from my_scripts.txt"""
    try:
        with open('my_scripts.txt', 'r', encoding='utf-8') as f:
            scripts = f.read()
    except FileNotFoundError:
        return "No reference scripts found"
    
    return """
HOOK STYLE ANALYSIS:

Pattern 1 - ASPIRATIONAL:
"अगर आपकी website ऐसी दिखती है… you're losing money daily."

Pattern 2 - PAIN POINT:
"Thinking to build an app? STOP."
"Most websites are just digital posters."

Pattern 3 - EXCLUSIVITY:
"90% startups fail online for THIS reason…"
"Your competitor is already doing THIS…"

Pattern 4 - SPECIFIC RESULT:
"Want clients in 7 days? Here's how."
"₹0 Ads, Still Getting Leads"

Pattern 5 - CURIOSITY GAP:
"Blockchain is not just crypto."
"AI is replacing teams… but smart founders are printing money."

STYLE NOTES:
- Mix Hindi/English naturally
- Use ellipsis (…) for pause
- ALL CAPS for emphasis
- Maximum 2 lines
- Direct, no fluff
- Creates immediate tension or curiosity
"""

def generate_hooks(topic, script_content):
    """Generate 5 hooks using Groq API"""
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ GROQ_API_KEY not found in .env file")
        sys.exit(1)
    
    client = Groq(api_key=api_key)
    
    hook_patterns = analyze_hook_style()
    
    system_prompt = f"""You are a viral hook writer. Study these patterns:

{hook_patterns}

Generate EXACTLY 5 hooks for this topic: {topic}

RULES:
- Each hook MUST be maximum 2 lines
- Must be speakable in under 4 seconds
- Mix Hindi and English (Hinglish) naturally
- Each hook uses a DIFFERENT pattern:
  Hook 1: ASPIRATIONAL (show better version)
  Hook 2: PAIN POINT (name frustration)
  Hook 3: EXCLUSIVITY (insider knowledge)
  Hook 4: SPECIFIC RESULT (number/time/money)
  Hook 5: CURIOSITY GAP (question they must watch to answer)

- NO generic openers like "Today I will" or "In this video"
- Use ellipsis (…) for dramatic pause
- ALL CAPS for emphasis words

Format each hook like this:
Hook 1: [hook text]
Pattern: ASPIRATIONAL
Confidence: [1-10]
Target: [who this works best for]

Script context:
{script_content[:300]}"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate 5 hooks for: {topic}"}
            ],
            temperature=0.8,
            max_tokens=800
        )
        
        hooks = completion.choices[0].message.content
        return hooks
        
    except Exception as e:
        print(f"❌ Groq API error: {str(e)}")
        sys.exit(1)

def main():
    print("=" * 60)
    print("AGENT 04: HOOK GENERATOR")
    print("=" * 60)
    
    # Read script and topic
    topic, script_content = read_script_and_topic()
    print(f"\n🎯 Topic: {topic}")
    print("\n⏳ Generating 5 hooks...")
    
    # Generate hooks
    hooks = generate_hooks(topic, script_content)
    
    # Save to file
    with open('hooks_output.txt', 'w', encoding='utf-8') as f:
        f.write(f"TOPIC: {topic}\n\n")
        f.write("=" * 60 + "\n")
        f.write(hooks)
        f.write("\n" + "=" * 60)
    
    # Print result
    print("\n" + "=" * 60)
    print("GENERATED HOOKS:")
    print("=" * 60)
    print(hooks)
    print("=" * 60)
    
    print(f"\n✅ Saved to hooks_output.txt")

if __name__ == "__main__":
    main()
