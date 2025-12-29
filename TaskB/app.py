from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# In-memory chat sessions
sessions = {}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    session_id = data.get("session_id", "default")
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "message is required"}), 400

    # create session if not exists
    if session_id not in sessions:
        sessions[session_id] = []

    # append user message
    sessions[session_id].append({
        "role": "user",
        "parts": [{"text": user_message}]
    })

    # call Gemini — IMPORTANT: pass list directly, not dict
    response = model.generate_content(sessions[session_id])

    bot_reply = response.text

    # save bot reply to session
    sessions[session_id].append({
        "role": "model",
        "parts": [{"text": bot_reply}]
    })

    return jsonify({
        "reply": bot_reply,
        "session_id": session_id
    })


@app.route("/")
def home():
    return "Gemini Chatbot API Running"


if __name__ == "__main__":
    app.run(debug=True)
