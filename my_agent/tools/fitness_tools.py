import json
import os
from datetime import datetime

FITNESS_FILE = "fitness_log.json"

def log_workout(
    exercise: str,
    sets: int,
    reps: int,
    weight_kg: float,
    notes: str = ""
) -> dict:
    """Logs a completed workout exercise to the fitness journal.
    
    Args:
        exercise: Name of the exercise e.g. 'Bench Press', 'Squat', 'Deadlift'.
        sets: Number of sets completed.
        reps: Number of reps per set.
        weight_kg: Weight used in kilograms.
        notes: Optional notes about the exercise e.g. 'felt strong', 'increase next time'.
    
    Returns:
        A dict confirming the workout was logged with full details.
    """
    data = _load_fitness_data()
    
    entry = {
        "id": len(data["workouts"]) + 1,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "exercise": exercise,
        "sets": sets,
        "reps": reps,
        "weight_kg": weight_kg,
        "total_volume_kg": sets * reps * weight_kg,
        "notes": notes,
    }
    
    data["workouts"].append(entry)
    _save_fitness_data(data)
    
    return {
        "logged": True,
        "entry_id": entry["id"],
        "exercise": exercise,
        "volume": f"{entry['total_volume_kg']} kg total volume",
        "message": f"Logged {sets}x{reps} {exercise} at {weight_kg}kg"
    }

def get_workout_history(exercise: str = None, days: int = 7) -> dict:
    """Retrieves workout history, optionally filtered by exercise.
    
    Args:
        exercise: Optional exercise name to filter by e.g. 'Bench Press'.
                 If not provided returns all exercises.
        days: Number of past days to retrieve. Default is 7.
    
    Returns:
        A dict with workout history, personal records and volume progress.
    """
    data = _load_fitness_data()
    workouts = data["workouts"]
    
    from datetime import timedelta
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    workouts = [w for w in workouts if w["date"] >= cutoff]
    
    if exercise:
        workouts = [w for w in workouts if exercise.lower() in w["exercise"].lower()]
    
    if not workouts:
        return {
            "found": False,
            "message": f"No workouts found in the last {days} days"
            + (f" for {exercise}" if exercise else "")
        }
    
    pr = max(workouts, key=lambda x: x["weight_kg"])
    
    total_volume = sum(w["total_volume_kg"] for w in workouts)
    
    return {
        "found": True,
        "total_sessions": len(workouts),
        "total_volume_kg": round(total_volume, 2),
        "personal_record": {
            "exercise": pr["exercise"],
            "weight_kg": pr["weight_kg"],
            "date": pr["date"],
        },
        "workouts": workouts[-10:], 
    }

def calculate_muscle_metrics(
    weight_kg: float,
    height_cm: float,
    age: int,
    goal_weight_kg: float = None
) -> dict:
    """Calculates key body metrics for muscle building goals.
    
    Args:
        weight_kg: Current body weight in kilograms.
        height_cm: Height in centimeters.
        age: Age in years.
        goal_weight_kg: Optional target body weight in kg.
    
    Returns:
        A dict with BMI, BMR, daily calorie targets and protein needs for muscle gain.
    """
    # BMI
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)
    
    if bmi < 18.5:
        bmi_category = "Underweight"
    elif bmi < 25:
        bmi_category = "Normal weight"
    elif bmi < 30:
        bmi_category = "Overweight"
    else:
        bmi_category = "Obese"
    
    bmr = round(10 * weight_kg + 6.25 * height_cm - 5 * age + 5)
    
    tdee = round(bmr * 1.55)
    
    muscle_gain_calories = tdee + 400
    
    protein_min = round(weight_kg * 1.8)
    protein_max = round(weight_kg * 2.2)
    
    result = {
        "current_weight_kg": weight_kg,
        "height_cm": height_cm,
        "bmi": bmi,
        "bmi_category": bmi_category,
        "bmr_kcal": bmr,
        "tdee_kcal": tdee,
        "muscle_gain_calories": muscle_gain_calories,
        "daily_protein_g": f"{protein_min}-{protein_max}g",
        "daily_water_liters": round(weight_kg * 0.033, 1),
    }
    
    if goal_weight_kg:
        kg_to_gain = round(goal_weight_kg - weight_kg, 1)
        weeks_estimate = round(abs(kg_to_gain) / 0.25)  
        result["goal_weight_kg"] = goal_weight_kg
        result["kg_to_gain"] = kg_to_gain
        result["estimated_weeks"] = weeks_estimate
        result["estimated_months"] = round(weeks_estimate / 4.3, 1)
    
    return result

def get_muscle_workout_plan(muscle_group: str) -> dict:
    """Returns a structured workout plan for a specific muscle group.
    
    Args:
        muscle_group: Target muscle group e.g. 'chest', 'back', 'legs', 
                     'shoulders', 'arms', 'full body'.
    
    Returns:
        A dict with a complete exercise plan including sets, reps and rest times.
    """
    plans = {
        "chest": {
            "muscle_group": "Chest",
            "focus": "Hypertrophy (muscle building)",
            "exercises": [
                {"exercise": "Bench Press", "sets": 4, "reps": "6-8", "rest_sec": 120, "tip": "Control the descent, explode up"},
                {"exercise": "Incline Dumbbell Press", "sets": 3, "reps": "8-10", "rest_sec": 90, "tip": "Keep shoulder blades retracted"},
                {"exercise": "Cable Flyes", "sets": 3, "reps": "12-15", "rest_sec": 60, "tip": "Squeeze at peak contraction"},
                {"exercise": "Dips", "sets": 3, "reps": "8-12", "rest_sec": 90, "tip": "Lean forward to hit chest more"},
            ]
        },
        "back": {
            "muscle_group": "Back",
            "focus": "Hypertrophy (muscle building)",
            "exercises": [
                {"exercise": "Deadlift", "sets": 4, "reps": "5-6", "rest_sec": 180, "tip": "Brace core, drive through heels"},
                {"exercise": "Pull-ups / Lat Pulldown", "sets": 4, "reps": "8-10", "rest_sec": 90, "tip": "Full stretch at bottom"},
                {"exercise": "Barbell Row", "sets": 3, "reps": "8-10", "rest_sec": 90, "tip": "Pull to lower chest, not belly"},
                {"exercise": "Cable Row", "sets": 3, "reps": "12-15", "rest_sec": 60, "tip": "Squeeze shoulder blades together"},
            ]
        },
        "legs": {
            "muscle_group": "Legs",
            "focus": "Hypertrophy (muscle building)",
            "exercises": [
                {"exercise": "Squat", "sets": 4, "reps": "6-8", "rest_sec": 180, "tip": "Break parallel, keep chest up"},
                {"exercise": "Romanian Deadlift", "sets": 3, "reps": "8-10", "rest_sec": 120, "tip": "Feel the hamstring stretch"},
                {"exercise": "Leg Press", "sets": 3, "reps": "10-12", "rest_sec": 90, "tip": "Full range of motion"},
                {"exercise": "Leg Curl", "sets": 3, "reps": "12-15", "rest_sec": 60, "tip": "Slow eccentric for growth"},
                {"exercise": "Calf Raise", "sets": 4, "reps": "15-20", "rest_sec": 60, "tip": "Full stretch, full contraction"},
            ]
        },
        "shoulders": {
            "muscle_group": "Shoulders",
            "focus": "Hypertrophy (muscle building)",
            "exercises": [
                {"exercise": "Overhead Press", "sets": 4, "reps": "6-8", "rest_sec": 120, "tip": "Don't flare elbows too wide"},
                {"exercise": "Lateral Raise", "sets": 4, "reps": "12-15", "rest_sec": 60, "tip": "Lead with elbows, not hands"},
                {"exercise": "Face Pull", "sets": 3, "reps": "15-20", "rest_sec": 60, "tip": "Great for rear delt and rotator cuff"},
                {"exercise": "Arnold Press", "sets": 3, "reps": "10-12", "rest_sec": 90, "tip": "Full rotation through the movement"},
            ]
        },
        "arms": {
            "muscle_group": "Arms (Biceps + Triceps)",
            "focus": "Hypertrophy (muscle building)",
            "exercises": [
                {"exercise": "Barbell Curl", "sets": 4, "reps": "8-10", "rest_sec": 90, "tip": "No swinging, strict form"},
                {"exercise": "Hammer Curl", "sets": 3, "reps": "10-12", "rest_sec": 60, "tip": "Hits brachialis for arm thickness"},
                {"exercise": "Tricep Pushdown", "sets": 4, "reps": "10-12", "rest_sec": 60, "tip": "Lock elbows in, full extension"},
                {"exercise": "Skull Crushers", "sets": 3, "reps": "10-12", "rest_sec": 90, "tip": "Control the bar on descent"},
                {"exercise": "Concentration Curl", "sets": 3, "reps": "12-15", "rest_sec": 60, "tip": "Peak contraction at top"},
            ]
        },
        "full body": {
            "muscle_group": "Full Body",
            "focus": "Compound hypertrophy",
            "exercises": [
                {"exercise": "Squat", "sets": 3, "reps": "6-8", "rest_sec": 180, "tip": "King of all exercises"},
                {"exercise": "Bench Press", "sets": 3, "reps": "6-8", "rest_sec": 120, "tip": "Control the descent"},
                {"exercise": "Deadlift", "sets": 3, "reps": "5-6", "rest_sec": 180, "tip": "Brace before every rep"},
                {"exercise": "Overhead Press", "sets": 3, "reps": "8-10", "rest_sec": 90, "tip": "Squeeze glutes for stability"},
                {"exercise": "Pull-ups", "sets": 3, "reps": "8-10", "rest_sec": 90, "tip": "Full dead hang at bottom"},
            ]
        },
    }
    
    key = muscle_group.lower()
    if key not in plans:
        return {
            "found": False,
            "message": f"No plan for '{muscle_group}'",
            "available": list(plans.keys())
        }
    
    plan = plans[key]
    plan["found"] = True
    plan["total_exercises"] = len(plan["exercises"])
    plan["estimated_duration_min"] = len(plan["exercises"]) * 12
    return plan

def _load_fitness_data() -> dict:
    if not os.path.exists(FITNESS_FILE):
        return {"workouts": [], "created": datetime.now().strftime("%Y-%m-%d")}
    with open(FITNESS_FILE, "r") as f:
        return json.load(f)

def _save_fitness_data(data: dict):
    with open(FITNESS_FILE, "w") as f:
        json.dump(data, f, indent=2)