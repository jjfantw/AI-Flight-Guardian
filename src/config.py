import json
import os
import logging

def load_tasks(filepath: str = "tasks.json") -> dict:
    """Load and parse the JSON task configuration."""
    if not os.path.exists(filepath):
        logging.error(f"Configuration file not found: {filepath}")
        return {"tasks": []}
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing {filepath}: {e}")
        return {"tasks": []}

def get_active_tasks(filepath: str = "tasks.json") -> list:
    """Return a list of strictly active tasks."""
    data = load_tasks(filepath)
    tasks = data.get("tasks", [])
    return [t for t in tasks if t.get("active", False)]
