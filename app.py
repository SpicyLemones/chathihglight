from flask import Flask, request, jsonify, render_template, redirect, url_for
import threading
import time

app = Flask(__name__)

# In-memory storage for chat messages and highlighted message
chat_messages = []
highlighted_message = None
highlight_reset_timer = None  # Timer for resetting the highlighted message


def reset_highlight():
    """
    Reset the highlighted message after a timeout.
    """
    global highlighted_message, highlight_reset_timer
    time.sleep(15)  # Wait for 15 seconds
    highlighted_message = None  # Reset the highlighted message
    highlight_reset_timer = None  # Clear the timer


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/highlight")
def highlight():
    # Check if there is a highlighted message with content
    if highlighted_message and highlighted_message.get("content"):
        return render_template("highlight.html", message=highlighted_message)
    else:
        # Redirect to the main page if no message is highlighted
        return redirect(url_for("index"))


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
    highlighted_message = request.json

    # Cancel the previous reset timer if it exists
    if highlight_reset_timer:
        highlight_reset_timer.cancel()

    # Start a new timer to reset the highlight after 20 seconds
    highlight_reset_timer = threading.Timer(20.0, lambda: reset_highlight())
    highlight_reset_timer.start()

    return jsonify({"status": "highlighted"}), 200


@app.route("/api/highlight", methods=["GET"])
def get_highlight():
    return jsonify(highlighted_message or {"author": "", "content": "No message highlighted yet."})


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

