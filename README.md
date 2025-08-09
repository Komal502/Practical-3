# Practical-3
# WebConf-Lite (Streamlit Demo)

WebConf-Lite is a Streamlit prototype inspired by popular web conferencing tools (schedule meetings, join a mock meeting room, chat, upload transcripts, and generate AI meeting summaries). This is intended as a deployable prototype for an assignment.

## Setup (local)
1. Clone the repo.
2. Create a Python venv:
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
3. Install:
   pip install -r requirements.txt
4. Set your OpenAI API key in environment:
   export OPENAI_API_KEY="sk-..."   # Linux/Mac
   setx OPENAI_API_KEY "sk-..."     # Windows (restart shell)
   or create a `.env` file with OPENAI_API_KEY=sk-...
5. Run:
   streamlit run streamlit_app.py

## Deploy on Streamlit Cloud
1. Push this repo to GitHub.
2. Go to https://share.streamlit.io, create a new app, connect your GitHub repo and branch, and set environment variable OPENAI_API_KEY in the Secrets section.

## Files
- streamlit_app.py : Main app
- ai_helpers.py : OpenAI helper functions (parsing + summarization)
- db.py : SQLite wrapper for meetings & chat

## Notes
- This prototype mocks real-time audio/video (embedding real streaming requires WebRTC & a backend). Instead we provide a meeting room UI, chat, and transcript + AI summarizer.
- For full production (real video), you would integrate a WebRTC stack (Janus/Mediasoup/Twilio/Agora) and secure token auth.

