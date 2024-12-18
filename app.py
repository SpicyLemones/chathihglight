from flask import Flask, request, jsonify, render_template, redirect, url_for
import threading

app = Flask(__name__)

# In-memory storage for chat messages and highlighted message
chat_messages = []
highlighted_message = None
highlight_reset_timer = None  # Timer for resetting the highlighted message


def reset_highlight():
    """
    Reset the highlighted message.
    """
    global highlighted_message, highlight_reset_timer
    highlighted_message = None
    highlight_reset_timer = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/highlight")
def highlight():
    return render_template("highlight.html")


@app.route("/api/chat", methods=["POST"])
def receive_chat():
    data = request.json
    chat_messages.append(data)  # Store the message
    return jsonify({"status": "success"}), 200


@app.route("/api/chat", methods=["GET"])
def get_chat():
    return jsonify(chat_messages)


@app.route("/api/highlight", methods=["POST"])
def set_highlight():
    global highlighted_message, highlight_reset_timer

    # Cancel the previous reset timer if it exists
    if highlight_reset_timer:
        highlight_reset_timer.cancel()

    # Update the highlighted message
    highlighted_message = request.json

    # Start a new timer to reset the highlight after 15 seconds
    highlight_reset_timer = threading.Timer(15.0, reset_highlight)
    highlight_reset_timer.start()

    return jsonify({"status": "highlighted"}), 200


@app.route("/api/highlight", methods=["GET"])
def get_highlight():
    return jsonify(highlighted_message or {"author": "", "content": ""})


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
