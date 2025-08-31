# fitness.py (Updated to accept profile data as an argument)
import argparse
import sqlite3
from datetime import datetime
import re
import json

import config 
import google.generativeai as genai

genai.configure(api_key=config.API_KEY)

DATABASE_NAME = 'fitness_tracker.db'

# --- AI & LOGIC FUNCTIONS ---
def get_nutritional_info(meal_name):
    # This function is unchanged
    print(f"🤖 Contacting AI to get nutrition info for '{meal_name}'...")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = f"""Provide a nutritional estimate for a standard serving of '{meal_name}'. Give me the data in a simple, parsable format like this:
        Calories: 500, Protein: 30g, Carbs: 60g, Fat: 20g
        Only provide this single line of data and nothing else."""
        response = model.generate_content(prompt)
        text_response = response.text
        calories = re.search(r"Calories: (\d+)", text_response)
        protein = re.search(r"Protein: (\d+)", text_response)
        carbs = re.search(r"Carbs: (\d+)", text_response)
        fat = re.search(r"Fat: (\d+)", text_response)
        return {"calories": int(calories.group(1)) if calories else None, "protein": int(protein.group(1)) if protein else None, "carbs": int(carbs.group(1)) if carbs else None, "fat": int(fat.group(1)) if fat else None}
    except Exception as e:
        print(f"Error contacting AI: {e}")
        return None

# --- MODIFIED AI TRANSFORMATION PLAN FUNCTION ---
def generate_transformation_plan(profile): # It now accepts a 'profile' dictionary
    """Generates a transformation plan based on the provided profile data."""
    print("🧠 Generating a transformation plan with user-provided data...")
    
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt1 = f"You are a fitness expert. A client's profile is: {json.dumps(profile)}. Is their goal realistic? Respond only with 'Possible' or 'Impossible' and a one-sentence justification."
    
    try:
        response1 = model.generate_content(prompt1)
        feasibility_response = response1.text.strip().lower()

        prompt2 = ""
        if 'impossible' in feasibility_response:
            prompt2 = f"The client's goal from profile {json.dumps(profile)} is unrealistic. Propose a new, safer timeline. Then generate a full 7-day meal and 5-day exercise plan for that new timeline, fitting their budget and location."
        else:
            prompt2 = f"The client's goal from profile {json.dumps(profile)} is achievable. Generate a full 7-day meal and 5-day exercise plan, fitting their budget and location."
        
        response2 = model.generate_content(prompt2)
        return response2.text
    except Exception as e:
        return f"❌ An error occurred while generating the plan: {e}"

def log_workout(exercise, sets, reps):
    # Unchanged
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO workouts (timestamp, exercise_name, sets, reps) VALUES (?, ?, ?, ?)', (datetime.now(), exercise, sets, reps))
    conn.commit()
    conn.close()
    print(f"✅ Logged Workout via Web: {sets} sets of {reps} {exercise}.")

def log_meal(name, calories, protein, carbs, fat):
    # Unchanged
    if name and not calories:
        ai_data = get_nutritional_info(name)
        if ai_data:
            calories, protein, carbs, fat = ai_data.get("calories"), ai_data.get("protein"), ai_data.get("carbs"), ai_data.get("fat")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO meals (timestamp, meal_name, calories, protein_grams, carbs_grams, fat_grams) VALUES (?, ?, ?, ?, ?, ?)', (datetime.now(), name, calories, protein, carbs, fat))
    conn.commit()
    conn.close()
    print(f"✅ Logged Meal via Web: {name}.")

def view_workouts():
    # Unchanged
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, exercise_name, sets, reps FROM workouts ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    output = []
    if not rows: return ["No workouts logged yet."]
    for row in rows:
        output.append(f"[{datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M')}] {row[1]}: {row[2]} sets of {row[3]} reps")
    return output

def view_meals():
    # Unchanged
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, meal_name, calories, protein_grams, carbs_grams, fat_grams FROM meals ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    output = []
    if not rows: return ["No meals logged yet."]
    for row in rows:
        details = f"Cals: {row[2] or 'N/A'}, Prot: {row[3] or 'N/A'}g, Carbs: {row[4] or 'N/A'}g, Fat: {row[5] or 'N/A'}g"
        output.append(f"[{datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M')}] {row[1]} ({details})")
    return output

def main():
    # The CLI main function is now slightly broken because `generate_transformation_plan` requires a profile.
    # This is okay, as our focus is the web app. We'll just have it print a message.
    parser = argparse.ArgumentParser(description="Your Personal Fitness Tracker CLI.")
    # ... rest of parser setup ...
    subparsers = parser.add_subparsers(dest='command', required=True, help="Main commands")
    log_parser = subparsers.add_parser('log', help="Log a new workout or meal")
    log_subparsers = log_parser.add_subparsers(dest='log_type', required=True, help="Type of item to log")
    workout_parser = log_subparsers.add_parser('workout', help="Log a new workout")
    workout_parser.add_argument('--exercise', type=str, required=True)
    workout_parser.add_argument('--sets', type=int, required=True)
    workout_parser.add_argument('--reps', type=int, required=True)
    meal_parser = log_subparsers.add_parser('meal', help="Log a new meal")
    meal_parser.add_argument('--name', type=str, required=True)
    meal_parser.add_argument('--calories', type=int, default=None)
    meal_parser.add_argument('--protein', type=int, default=None)
    meal_parser.add_argument('--carbs', type=int, default=None)
    meal_parser.add_argument('--fat', type=int, default=None)
    view_parser = subparsers.add_parser('view', help="View logged workouts or meals")
    view_parser.add_argument('item_type', choices=['workouts', 'meals'])
    plan_parser = subparsers.add_parser('plan', help="Generate a new transformation plan based on your profile")
    args = parser.parse_args()
    if args.command == 'log':
        if args.log_type == 'workout': log_workout(args.exercise, args.sets, args.reps)
        elif args.log_type == 'meal': log_meal(args.name, args.calories, args.protein, args.carbs, args.fat)
    elif args.command == 'view':
        if args.item_type == 'workouts': [print(line) for line in view_workouts()]
        elif args.item_type == 'meals': [print(line) for line in view_meals()]
    elif args.command == 'plan':
        print("Please use the web app (app.py) to generate a plan.")

if __name__ == '__main__':
    main()