from flask import Flask, render_template, request, jsonify
from agents import CustomerHelperAgent

app = Flask(__name__)
agent = CustomerHelperAgent()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Please enter a customer message."}), 400

    try:
        result = agent.handle_message(message)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "error": "The AI service could not process the request.",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    print("Customer Helper Agent is running.")
    print("Open http://127.0.0.1:5000 in your browser.")
    app.run(debug=True)
