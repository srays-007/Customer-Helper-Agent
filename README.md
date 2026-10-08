# Customer Helper Agent

A Python + Flask + Google Gemini customer-support assistant.

## Architecture

Customer
  -> Web UI
  -> Flask
  -> Coordinator
  -> Intent Agent
  -> Reply Agent
  -> Customer

The application also keeps short-term conversation memory and flags high-urgency requests for human escalation.

## Setup

1. Install Python 3.10+.
2. Create a virtual environment.
3. Install dependencies:
   pip install -r requirements.txt
4. Create a `.env` file from `.env.example`.
5. Add your Gemini API key.
6. Run:
   python app.py
7. Open:
   http://127.0.0.1:5000

## Example test messages

- I want to cancel my subscription.
- My invoice amount is wrong.
- Where is my order?
- I need a refund.
- My money was deducted but my order failed.

## Important

The conversation memory is stored only in the running Python process. It is not a database and is cleared when the server restarts.
