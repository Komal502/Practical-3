import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import db
from ai_helpers import parse_meeting_nl, summarize_transcript
import json

st.set_page_config(page_title="WebConf-Lite", layout="wide")

# --- Sidebar ---
st.sidebar.title("WebConf-Lite")
st.sidebar.markdown("Prototype web conferencing app (mock video).")
st.sidebar.markdown("AI: meeting parsing & summary (requires OPENAI_API_KEY).")
mode = st.sidebar.selectbox("Mode", ["Dashboard", "Create meeting (NL)", "Meeting room", "Upload transcript"])

# --- Dashboard ---
if mode == "Dashboard":
    st.header("Meetings Dashboard")
    meetings = db.list_meetings()
    if not meetings:
        st.info("No meetings yet. Create one using 'Create meeting (NL)'")
    else:
        df = pd.DataFrame(meetings)
        st.dataframe(df[['id','title','start_time','duration_minutes','host']])
        sel = st.number_input("Enter Meeting ID to join (Meeting room)", min_value=0, step=1)
        if st.button("Go to Meeting room"):
            st.session_state.setdefault("join_meeting_id", sel)
            st.experimental_rerun()

# --- Create meeting via NL ---
if mode == "Create meeting (NL)":
    st.header("Create meeting using natural language")
    text = st.text_area("Describe meeting (e.g. 'Sprint planning tomorrow at 10am for 30 minutes with team')", height=120)
    if st.button("Parse & Create"):
        if not text.strip():
            st.error("Please enter text.")
        else:
            res = parse_meeting_nl(text)
            # safe defaults
            title = res.get("title") or text[:60]
            start_time = res.get("start_time") or ""
            duration = int(res.get("duration_minutes") or 30)
            description = res.get("description") or ""
            host = "You"
            meeting_id = db.create_meeting(title, description, start_time, duration, host)
            st.success(f"Created meeting id={meeting_id}")
            st.info("You can go to Dashboard to view/join the meeting.")

# --- Meeting room ---
if mode == "Meeting room":
    st.header("Meeting Room (mock)")
    mtg_id = st.number_input("Meeting ID", min_value=1, step=1, value=st.session_state.get("join_meeting_id", 1))
    if st.button("Load meeting"):
        st.session_state['join_meeting_id'] = mtg_id
        st.experimental_rerun()

    meeting_id = st.session_state.get("join_meeting_id", mtg_id)
    meetings = db.list_meetings()
    meeting = next((m for m in meetings if m['id'] == meeting_id), None)
    if not meeting:
        st.warning("Meeting not found. Create one first.")
    else:
        st.subheader(meeting['title'])
        st.write("Description:", meeting['description'])
        left, right = st.columns([3,2])
        with left:
            st.info("Video area (mock). For a full product integrate WebRTC/Aggregator like Agora/Twilio.")
            st.image("https://via.placeholder.com/800x450.png?text=Mock+Video+Area", use_column_width=True)
            st.text_input("Say something (this will be posted to meeting chat)", key=f"say_{meeting_id}")
            if st.button("Post to chat", key=f"post_{meeting_id}"):
                text = st.session_state.get(f"say_{meeting_id}", "")
                if text.strip():
                    db.add_chat(meeting_id, "You", text)
                    st.experimental_rerun()
        with right:
            st.write("Chat")
            chat_msgs = db.get_chat(meeting_id)
            for m in chat_msgs:
                st.write(f"**{m['sender']}**: {m['message']}")
            st.markdown("---")
            st.write("Quick actions")
            if st.button("Generate summary from chat"):
                transcript = "\n".join([f"{m['sender']}: {m['message']}" for m in chat_msgs])
                if not transcript.strip():
                    st.warning("No chat to summarize.")
                else:
                    with st.spinner("Generating summary..."):
                        out = summarize_transcript(transcript)
                    st.write("**Summary:**")
                    st.write(out.get("summary", ""))
                    st.write("**Action items:**")
                    st.write(out.get("action_items", []))
                    st.write("**Decisions:**")
                    st.write(out.get("decisions", []))

# --- Upload transcript & summarize ---
if mode == "Upload transcript":
    st.header("Upload meeting transcript (txt) and summarize")
    uploaded = st.file_uploader("Upload transcript (.txt) or paste below", type=["txt"])
    transcript_text = ""
    if uploaded:
        transcript_text = uploaded.read().decode("utf-8")
    else:
        transcript_text = st.text_area("Or paste transcript here", height=300)

    if st.button("Summarize transcript"):
        if not transcript_text.strip():
            st.error("Provide transcript text.")
        else:
            with st.spinner("Summarizing..."):
                out = summarize_transcript(transcript_text)
            st.subheader("Summary")
            st.write(out.get("summary", ""))
            st.subheader("Action Items")
            for ai in out.get("action_items", []):
                st.write("- " + (ai if isinstance(ai, str) else str(ai)))
            st.subheader("Decisions")
            for d in out.get("decisions", []):
                st.write("- " + (d if isinstance(d, str) else str(d)))
