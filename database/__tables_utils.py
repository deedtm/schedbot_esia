def format_values(values: dict) -> str:
    formatted_values = []
    for v in values.values():
        if isinstance(v, str):
            formatted_values.append(f"'{v}'")
        elif v is None:
            formatted_values.append("NULL")
        else:
            formatted_values.append(str(v))
    return ", ".join(formatted_values)
