from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# In-memory storage for chat messages and highlighted message
chat_messages = []
highlighted_message = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/highlight")
def highlight():
    return render_template("highlight.html", message=highlighted_message)


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
    global highlighted_message
    highlighted_message = request.json
    return jsonify({"status": "highlighted"}), 200


@app.route("/api/highlight", methods=["GET"])
def get_highlight():
    return jsonify(highlighted_message or {"author": "", "content": "No message highlighted yet."})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
