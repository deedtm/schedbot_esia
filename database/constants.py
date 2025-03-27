import json


with open("database/queries.json", "r", encoding="utf8") as f:
    QUERIES: dict[str, dict[str, str]] = json.load(f)

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
