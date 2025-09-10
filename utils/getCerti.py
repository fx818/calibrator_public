path = "allsaves/saves_0.txt"
from dotenv import load_dotenv
load_dotenv()

import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
import json
import re


certificate_schema = {
    "type": "object",
    "properties": {
        "certificate_number": {"type": "string"},
        "issue_date": {"type": "string"},
        "customer": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "address": {"type": "string"}
            },
            "required": ["name", "address"]
        },
        "duc": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "serial_number": {"type": ["string", "null"]},
                "make_model": {"type": "string"},
                "range": {"type": "string"},
                "least_count": {"type": "number"},
                "condition_at_receipt": {"type": "string"},
                "location": {"type": "string"}
            },
            "required": ["id", "make_model", "range", "least_count", "condition_at_receipt", "location"]
        },
        "calibration": {
            "type": "object",
            "properties": {
                "done_at": {"type": "string"},
                "date": {"type": "string"},
                "next_due": {"type": "string"},
                "date_received": {"type": "string"},
                "procedure_references": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "environmental_conditions": {
                    "type": "object",
                    "properties": {
                        "temperature_c": {"type": "number"},
                        "relative_humidity_percent": {"type": "number"}
                    },
                    "required": ["temperature_c", "relative_humidity_percent"]
                }
            },
            "required": ["done_at", "date", "next_due", "date_received", "procedure_references", "environmental_conditions"]
        },
        "standard_equipment": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "id": {"type": "string"},
                "serial_number": {"type": ["string", "null"]},
                "certificate_number": {"type": "string"},
                "calibration_date": {"type": "string"},
                "calibration_due_date": {"type": "string"}
            },
            "required": ["name", "id", "certificate_number", "calibration_date", "calibration_due_date"]
        },
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "duc_value": {"type": "number"},
                    "std_value": {"type": "number"},
                    "error": {"type": "number"},
                    "expanded_uncertainty": {"type": "number"}
                },
                "required": ["duc_value", "std_value", "error", "expanded_uncertainty"]
            }
        },
        "remarks": {"type": "string"},
        "notes": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["certificate_number", "issue_date", "customer", "duc", "calibration", "standard_equipment", "results", "remarks", "notes"],
    "additionalProperties": False
}


# Load your big unstructured text
with open("saves.txt", "r", encoding="cp1252") as f:
    all_text = f.read()

# Split by "Unique Lab Report No." (marker for each certificate)
cert_texts = re.split(r"(?=Unique Lab Report No\.)", all_text)
cert_texts = [c.strip() for c in cert_texts if c.strip()]

print(f"🔎 Found {len(cert_texts)} certificates")
for i, cert_text in enumerate(cert_texts, start=1):
    response = client.responses.create(
        model="moonshotai/kimi-k2-instruct",
        instructions="Extract the certificate details from the text according to the provided JSON schema.",
        input=cert_text,
        text={
            "format": {
                "type": "json_schema",
                "name": "certificate_data",
                "schema": certificate_schema
            }
        }
    )
    # Groq sometimes returns code fences; remove if present
    raw_text = response.output_text.strip()
    if raw_text.startswith("```"):
        raw_text = "\n".join(raw_text.splitlines()[1:-1])

    # Parse to Python dict
    try:
        parsed_output = json.loads(raw_text)
    except json.JSONDecodeError:
        parsed_output = {"raw_text": raw_text}

    # Save JSON file
    filename = f"certificates/certificate_{i}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(parsed_output, f, indent=4, ensure_ascii=False)

    print(f"✅ Saved {filename}")