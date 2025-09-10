import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

with open("saves2.txt", "r", encoding="utf-8") as f:
    all_cert_text = f.read()

# JSON schema (from previous example)

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


def get_certificate_data(all_cert_text):
    response = client.responses.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        instructions="""
    You are given a large text containing multiple calibration certificates. 
    Extract each certificate as a separate JSON object following the schema provided.
    Return a single JSON array, where each element is one certificate.
    """,
        input=all_cert_text,
        text={
            "format": {
                "type": "json_schema",
                "name": "all_certificates",
                "schema": {
                    "type": "array",
                    "items": certificate_schema
                }
            }
        }
    )

    # Parse the output
    raw_text = response.output_text.strip()
    # Remove code fences if present
    if raw_text.startswith("```"):
        raw_text = "\n".join(raw_text.splitlines()[1:-1])
    # Try to extract the JSON array part
    try:
        # Find the first "[" and the last "]" → that's the array
        start = raw_text.find("[")
        end = raw_text.rfind("]") + 1
        json_str = raw_text[start:end]
        certificates_list = json.loads(json_str)
    except Exception as e:
        print("⚠️ Could not parse properly, saving raw output instead:", e)
        certificates_list = [{"raw_text": raw_text}]

    # Save all certificates as one JSON file
    with open("all_certificatesModelOSS.json", "w", encoding="utf-8") as f:
        json.dump(certificates_list, f, indent=4, ensure_ascii=False)

    print(f"✅ Extracted {len(certificates_list)} certificates")
    return certificates_list