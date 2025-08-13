# app/routes/chatbot.py
from fastapi import APIRouter, Request
import spacy
import re

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

router = APIRouter()

def detect_intent(user_text: str) -> str:
    """
    Identify basic intents from the user message.
    You can expand this with more keywords or patterns.
    """
    text_lower = user_text.lower()

    if "add leave" in text_lower or "assign leave" in text_lower or "request leave" in text_lower:
        return "add_leave"
    elif "delete user" in text_lower or "remove user" in text_lower or "delete employee" in text_lower:
        return "delete_user"
    elif "show report" in text_lower or "leave report" in text_lower:
        return "show_report"
    elif "hi" in text_lower or "hello" in text_lower:
        return "greet"
    else:
        return "unknown"

@router.post("/admin/chatbot")
async def admin_chatbot(request: Request):
    """
    Process chatbot messages using spaCy NER for entity extraction
    and simple keyword rules for intent detection.
    """
    data = await request.json()
    user_text = data.get("text", "").strip()

    if not user_text:
        return {"error": "No message text provided"}

    # Run text through spaCy pipeline
    doc = nlp(user_text)

    # Extract People and Dates
    people = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    dates = [ent.text for ent in doc.ents if ent.label_ in ["DATE", "TIME"]]

    # Detect intent
    intent = detect_intent(user_text)

    # Placeholder bot reply – later we map directly to admin_leave.py functions
    reply_parts = [f"Detected intent: {intent}"]
    if people:
        reply_parts.append(f"Names: {people}")
    if dates:
        reply_parts.append(f"Dates/times: {dates}")

    reply_text = " | ".join(reply_parts)

    return {
        "user_message": user_text,
        "intent": intent,
        "entities": {
            "people": people,
            "dates": dates
        },
        "bot_reply": reply_text
    }
