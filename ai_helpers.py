import os
import openai
from typing import Tuple, Dict

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not set. AI features will fail.")
openai.api_key = OPENAI_API_KEY

def parse_meeting_nl(text: str) -> Dict:
    """
    Parse natural language meeting creation text into structured fields.
    Example input: "Meet with team tomorrow at 3pm for 45 minutes about sprint planning"
    Returns dict: {title, start_time (ISO string guess), duration_minutes, description}
    """
    prompt = f"""
You are a helpful parser. Extract these fields from the user sentence: title, start_time (in ISO date or natural form), duration_minutes (integer), description.
If a field isn't present, return an empty string or 0 for duration.
Input: \"\"\"{text}\"\"\"

Return a JSON object only.
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.0,
        max_tokens=200
    )
    content = resp.choices[0].message.content.strip()
    # Try to parse JSON safely (some models return proper JSON; otherwise we fallback naive)
    import json
    try:
        j = json.loads(content)
    except Exception:
        # naive fallback - put entire text as title
        j = {"title": text, "start_time": "", "duration_minutes": 0, "description": ""}
    return j

def summarize_transcript(transcript_text: str) -> str:
    """
    Ask the model to generate a short meeting summary, action items and decisions.
    """
    prompt = f"""
You are an assistant that creates concise meeting outputs.
Input transcript:
\"\"\"{transcript_text}\"\"\"

Produce JSON with fields:
- summary: 2-4 sentence concise summary
- action_items: list of short action items (who - task - due if present)
- decisions: list of decisions
Return JSON only.
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.2,
        max_tokens=400
    )
    content = resp.choices[0].message.content.strip()
    import json
    try:
        j = json.loads(content)
        return j
    except Exception:
        # fallback: ask for plain text summary
        resp2 = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":f"Summarize the following in 3 sentences:\n\n{transcript_text}"}],
            temperature=0.2,
            max_tokens=200
        )
        return {"summary": resp2.choices[0].message.content.strip(), "action_items": [], "decisions": []}
