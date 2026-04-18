AI CONTENT GENERATOR
====================

QUICK START (LOCAL)
-------------------
./start_web.sh
Open: http://localhost:5000

DEPLOY TO RENDER
----------------
1. Push to GitHub
2. Connect repo on Render.com
3. Add environment variable: GROQ_API_KEY
4. Deploy!

FILES
-----
app.py              - Flask web server
voice_writer.py     - Script generator
hook_generator.py   - Hook creator
templates/          - HTML
static/             - CSS + JS
my_scripts.txt      - Your voice samples
iguser.txt          - Instagram targets
.env                - API key (local)
Procfile            - Render start command
runtime.txt         - Python version
requirements.txt    - Dependencies
