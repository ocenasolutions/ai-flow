#!/usr/bin/env python3
"""
Flask Web App for AI Content Generation
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

def analyze_voice_patterns():
    """Analyze my_scripts.txt to extract voice patterns"""
    try:
        with open('my_scripts.txt', 'r', encoding='utf-8') as f:
            scripts = f.read()
    except FileNotFoundError:
        return "No reference scripts found"
    
    return """
VOICE ANALYSIS:
- Uses Hinglish mix naturally (अगर, ऐसी, etc.)
- Direct, no-fluff language
- Business terms: "conversion", "funnel", "automation", "system"
- Currency in ₹ (rupees)
- Strong action words: "STOP", "NO", "gone", "waste"
- Very short, punchy lines (3-7 words average)
- Uses "→" for flow/progression
- Lists with "No X / No Y / No Z" pattern
- Rhetorical questions followed by answers
- Always ends with clear CTA: "DM '[KEYWORD]' — [what they get]"
- 80% English, 20% Hindi
- Authoritative but not arrogant
- Urgent without being pushy
"""

def generate_script(topic):
    """Generate script using Groq API"""
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return {"error": "GROQ_API_KEY not found in .env file"}
    
    client = Groq(api_key=api_key)
    voice_patterns = analyze_voice_patterns()
    
    system_prompt = f"""You are a script writer who writes EXACTLY in this creator's voice:

{voice_patterns}

CRITICAL RULES:
- Write in the EXACT style shown above
- Mix Hindi and English naturally (Hinglish)
- Keep sentences SHORT and PUNCHY
- NO generic openers like "Today I will" or "In this video"
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
        
        return {"script": completion.choices[0].message.content}
        
    except Exception as e:
        return {"error": str(e)}

def generate_hooks(topic, script_content):
    """Generate 5 hooks using Groq API"""
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        return {"error": "GROQ_API_KEY not found in .env file"}
    
    client = Groq(api_key=api_key)
    
    hook_patterns = """
HOOK STYLE PATTERNS:
Pattern 1 - ASPIRATIONAL: "अगर आपकी website ऐसी दिखती है… you're losing money daily."
Pattern 2 - PAIN POINT: "Thinking to build an app? STOP."
Pattern 3 - EXCLUSIVITY: "90% startups fail online for THIS reason…"
Pattern 4 - SPECIFIC RESULT: "Want clients in 7 days? Here's how."
Pattern 5 - CURIOSITY GAP: "AI is replacing teams… but smart founders are printing money."

STYLE NOTES:
- Mix Hindi/English naturally
- Use ellipsis (…) for pause
- ALL CAPS for emphasis
- Maximum 2 lines
- Direct, no fluff
- Creates immediate tension or curiosity
"""
    
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
        
        return {"hooks": completion.choices[0].message.content}
        
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Generate content endpoint"""
    try:
        data = request.json
        topic = data.get('topic', 'AI automation for businesses')
        
        # Generate script
        script_result = generate_script(topic)
        if 'error' in script_result:
            return jsonify(script_result), 500
        
        # Generate hooks
        hooks_result = generate_hooks(topic, script_result['script'])
        if 'error' in hooks_result:
            return jsonify(hooks_result), 500
        
        # Return results (no file saving)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'topic': topic,
            'script': script_result['script'],
            'hooks': hooks_result['hooks'],
            'timestamp': timestamp
        })
    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # Get port from environment variable (for deployment) or use 5000
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 60)
    print("🚀 AI CONTENT GENERATOR - WEB APP")
    print("=" * 60)
    print("\n✅ Server starting...")
    print(f"📱 Open in browser: http://localhost:{port}")
    print("\n⏹️  Press Ctrl+C to stop\n")
    
    # Use debug=False in production
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
