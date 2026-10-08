import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from memory import ConversationMemory

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Put your Gemini API key in the .env file."
    )

MODEL_NAME = "gemini-3.5-flash-lite"

client = genai.Client(api_key=API_KEY)


def generate_with_retry(prompt, max_attempts=3):
    """Call Gemini and retry a few times for temporary API errors."""
    delays = [1, 2, 4]

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            if not response.text:
                raise RuntimeError("Gemini returned an empty response.")
            return response.text.strip()

        except Exception:
            if attempt == max_attempts - 1:
                raise
            time.sleep(delays[attempt])


class IntentAgent:
    """Agent responsible for classifying the customer's problem."""

    def classify(self, message):
        prompt = f"""
You are an intent and urgency classifier for a customer support system.

Customer message:
{message}

Classify the message using ONLY these values.

intent:
- refund
- cancellation
- billing
- shipping
- general_help
- general

urgency:
- high
- medium
- low

Return ONLY valid JSON in this exact structure:
{{
  "intent": "billing",
  "urgency": "high"
}}

Do not add markdown or explanation.
"""

        # Structured JSON output makes the classifier easier for the
        # application to process reliably.
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "intent": {
                            "type": "STRING",
                            "enum": [
                                "refund",
                                "cancellation",
                                "billing",
                                "shipping",
                                "general_help",
                                "general",
                            ],
                        },
                        "urgency": {
                            "type": "STRING",
                            "enum": ["high", "medium", "low"],
                        },
                    },
                    "required": ["intent", "urgency"],
                },
            ),
        )

        result = json.loads(response.text)
        return result["intent"], result["urgency"]


class ReplyAgent:
    """Agent responsible for generating the customer-facing reply."""

    def create_reply(self, message, intent, urgency, history):
        prompt = f"""
You are a professional customer support assistant.

Customer message:
{message}

Detected intent:
{intent}

Detected urgency:
{urgency}

Recent conversation history:
{history}

Write a short, empathetic and professional reply.

Rules:
1. Acknowledge the customer's issue.
2. Give a useful next step when possible.
3. Ask for ONE piece of information if it is needed.
4. Do not invent order numbers, refunds, policies or actions.
5. Keep the reply to 2-4 sentences.
6. Do not mention that you are an AI or that another agent classified the message.
"""

        return generate_with_retry(prompt)


class CustomerHelperAgent:
    """Coordinator that connects memory, classification and reply generation."""

    def __init__(self):
        self.intent_agent = IntentAgent()
        self.reply_agent = ReplyAgent()
        self.memory = ConversationMemory()

    def handle_message(self, message):
        self.memory.add("user", message)

        # Step 1: understand the customer's request.
        intent, urgency = self.intent_agent.classify(message)

        # Step 2: use recent conversation context when generating the reply.
        history = self.memory.get_context()

        # Step 3: generate the response.
        reply = self.reply_agent.create_reply(
            message, intent, urgency, history
        )

        self.memory.add("agent", reply)

        # Step 4: high urgency can be escalated to human support.
        escalation = urgency == "high"

        return {
            "intent": intent,
            "urgency": urgency,
            "reply": reply,
            "escalation": escalation,
            "model": MODEL_NAME,
        }
