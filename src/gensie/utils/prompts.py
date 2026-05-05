import json
from typing import Any, Dict, Optional


def generate_blank_template(schema: Dict[str, Any]) -> Any:
    """
    Recursively generates a blank JSON object template from a JSON Schema.
    """
    # Handle $ref if present (though simple schemas might not have them)
    # This is a simplified version; for complex schemas, use a library or resolve refs.

    if "type" not in schema:
        # Check for anyOf, allOf, etc. if needed
        if "anyOf" in schema:
            return generate_blank_template(schema["anyOf"][0])
        return None

    schema_type = schema["type"]

    if schema_type == "object":
        template = {}
        properties = schema.get("properties", {})
        for prop_name, prop_schema in properties.items():
            template[prop_name] = generate_blank_template(prop_schema)
        return template
    elif schema_type == "array":
        items = schema.get("items", {})
        if items:
            # We provide a single empty element to show structure
            return [generate_blank_template(items)]
        return []
    elif schema_type == "string":
        return ""
    elif schema_type == "number" or schema_type == "integer":
        return 0
    elif schema_type == "boolean":
        return False
    else:
        return None


def format_end_anchored_prompt(
    instruction: str, schema: Dict[str, Any], input_text: str, delimiter: str = "###"
) -> str:
    """
    Formats a prompt using the End-Anchored Template strategy.
    """
    blank_template = generate_blank_template(schema)
    template_json = json.dumps(blank_template, indent=2)

    prompt = (
        f"{delimiter} INSTRUCTIONS\n"
        f"{instruction}\n\n"
        f"{delimiter} SCHEMA\n"
        f"{json.dumps(schema, indent=2)}\n\n"
        f"{delimiter} CONTEXT\n"
        f"{input_text}\n\n"
        f"{delimiter} RESPONSE TEMPLATE\n"
        f"Please fill the following JSON template based on the CONTEXT above. "
        f"Provide ONLY the JSON object.\n\n"
        f"{template_json}"
    )
    return prompt
