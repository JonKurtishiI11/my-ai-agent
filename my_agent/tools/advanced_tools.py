import json
import urllib.request
import urllib.parse
from datetime import datetime

def get_weather(city: str) -> dict:
    """Gets current weather for a city using a free API.
    
    Args:
        city: Name of the city to get weather for.
    
    Returns:
        A dict with temperature, description and humidity.
    """
    try:
        city_encoded = urllib.parse.quote(city)
        url = f"https://wttr.in/{city_encoded}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read())
        current = data["current_condition"][0]
        return {
            "city": city,
            "temp_c": current["temp_C"],
            "temp_f": current["temp_F"],
            "description": current["weatherDesc"][0]["value"],
            "humidity": current["humidity"],
            "feels_like_c": current["FeelsLikeC"],
        }
    except Exception as e:
        return {"error": str(e), "city": city}

def save_note(title: str, content: str) -> dict:
    """Saves a note to a local JSON file.   
    
    Args:
        title: The title of the note.
        content: The content of the note.
    
    Returns:
        A dict confirming the note was saved.
    """
    import os
    notes_file = "notes.json"
    notes = []
    if os.path.exists(notes_file):
        with open(notes_file, "r") as f:
            notes = json.load(f)
    note = {
        "id": len(notes) + 1,
        "title": title,
        "content": content,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    notes.append(note)
    with open(notes_file, "w") as f:
        json.dump(notes, f, indent=2)
    return {"saved": True, "note_id": note["id"], "title": title}

def list_notes() -> dict:
    """Lists all saved notes.
    
    Returns:
        A dict with all saved notes.
    """
    import os
    notes_file = "notes.json"
    if not os.path.exists(notes_file):
        return {"notes": [], "count": 0}
    with open(notes_file, "r") as f:
        notes = json.load(f)
    return {"notes": notes, "count": len(notes)}

def calculate_advanced(expression: str) -> dict:
    """Evaluates a math expression including advanced operations.
    
    Args:
        expression: Math expression e.g. '25 * 48' or '100 / 4 + 20'.
    
    Returns:
        A dict with the result.
    """
    try:
        import math
        allowed_names = {k: v for k, v in math.__dict__.items() 
                        if not k.startswith("__")}
        allowed_names.update({"abs": abs, "round": round})
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return {"result": result, "expression": expression}
    except Exception as e:
        return {"error": str(e), "expression": expression}

def convert_units(value: float, from_unit: str, to_unit: str) -> dict:
    """Converts between common units.
    
    Args:
        value: The numeric value to convert.
        from_unit: The unit to convert from (e.g. 'km', 'kg', 'celsius').
        to_unit: The unit to convert to (e.g. 'miles', 'lbs', 'fahrenheit').
    
    Returns:
        A dict with the converted value.
    """
    conversions = {
        ("km", "miles"): lambda x: x * 0.621371,
        ("miles", "km"): lambda x: x * 1.60934,
        ("kg", "lbs"): lambda x: x * 2.20462,
        ("lbs", "kg"): lambda x: x * 0.453592,
        ("celsius", "fahrenheit"): lambda x: x * 9/5 + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
        ("meters", "feet"): lambda x: x * 3.28084,
        ("feet", "meters"): lambda x: x * 0.3048,
    }
    key = (from_unit.lower(), to_unit.lower())
    if key not in conversions:
        return {"error": f"Conversion from {from_unit} to {to_unit} not supported"}
    result = conversions[key](value)
    return {
        "original": f"{value} {from_unit}",
        "converted": f"{round(result, 4)} {to_unit}"
    }