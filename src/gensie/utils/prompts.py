from typing import Any, Dict


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
