import os
from flask import Flask, request, jsonify
import requests

API_KEY = os.environ.get("API_KEY", "PASTE_YOUR_GROQ_KEY_HERE")
MODEL = "openai/gpt-oss-120b"

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>My AI Chat</title>
<style>
  body { margin:0; font-family:sans-serif; background:#f4f4f4; display:flex; flex-direction:column; height:100vh; height:100dvh; }
  #bar { flex-shrink:0; }
  h1 { margin:0; padding:12px; background:#10a37f; color:#fff; font-size:18px; }
  #chat { flex:1; overflow-y:auto; padding:10px; }
  .msg { max-width:80%; padding:10px 12px; margin:6px 0; border-radius:12px; white-space:pre-wrap; }
  .user { background:#10a37f; color:#fff; margin-left:auto; }
  .bot { background:#fff; color:#222; }
  #bar { display:flex; padding:8px; background:#fff; }
  #text { flex:1; padding:10px; font-size:16px; border:1px solid #ccc; border-radius:8px; }
  button { margin-left:8px; padding:10px 16px; background:#10a37f; color:#fff; border:0; border-radius:8px; font-size:16px; }
</style>
</head>
<body>
<h1>My AI Chat</h1>
<div id="chat"></div>
<div id="bar">
  <input id="text" placeholder="Type a message..." onkeydown="if(event.key==='Enter')send()">
  <button onclick="send()">Send</button>
</div>
<script>
let history = [];
const chat = document.getElementById("chat");
const box = document.getElementById("text");

function add(cls, txt) {
  const d = document.createElement("div");
  d.className = "msg " + cls;
  d.textContent = txt;
  chat.appendChild(d);
  chat.scrollTop = chat.scrollHeight;
  return d;
}

async function send() {
  const msg = box.value.trim();
  if (!msg) return;
  box.value = "";
  add("user", msg);
  history.push({ role: "user", text: msg });
  const wait = add("bot", "...");
  try {
    const r = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ history: history })
    });
    const data = await r.json();
    wait.textContent = data.reply;
    history.push({ role: "model", text: data.reply });
  } catch (e) {
    wait.textContent = "Error: " + e;
  }
}
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return PAGE


@app.route("/chat", methods=["POST"])
def chat():
    history = request.json.get("history", [])
    messages = [
        {
            "role": "assistant" if m["role"] == "model" else "user",
            "content": m["text"],
        }
        for m in history
    ]
    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": "Bearer " + API_KEY},
            json={"model": MODEL, "messages": messages},
            timeout=60,
        )
        data = res.json()
        reply = data["choices"][0]["message"]["content"]
    except Exception:
        reply = "Sorry, something went wrong: " + str(locals().get("data", ""))
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
