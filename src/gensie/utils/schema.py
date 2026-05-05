from typing import Dict, Any

def compress_schema_to_ts(schema: Dict[str, Any], indent_level: int = 0) -> str:
    """
    Compresses a JSON schema into a concise TypeScript type representation.
    """
    schema_type = schema.get("type", "any")

    if schema_type == "object":
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        
        if not properties:
            return "Record<string, any>"
            
        lines = ["{"]
        indent = "  " * (indent_level + 1)
        for prop, prop_schema in properties.items():
            is_optional = "?" if prop not in required else ""
            prop_ts = compress_schema_to_ts(prop_schema, indent_level + 1)
            lines.append(f"{indent}{prop}{is_optional}: {prop_ts};")
            
        lines.append("  " * indent_level + "}")
        return "\n".join(lines)
        
    elif schema_type == "array":
        items = schema.get("items", {})
        item_ts = compress_schema_to_ts(items, indent_level)
        if " " in item_ts or "\n" in item_ts:
            return f"Array<{item_ts}>"
        return f"{item_ts}[]"
        
    elif schema_type in ("integer", "number"):
        return "number"
    elif schema_type == "string":
        return "string"
    elif schema_type == "boolean":
        return "boolean"
    else:
        return "any"
