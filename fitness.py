import argparse
import sqlite3
from datetime import datetime
import re
import json

# --- AI Setup (for both local and cloud) ---
import streamlit as st
import google.generativeai as genai

try:
    # Get API key from Streamlit secrets
    api_key = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    # Fallback to local config file
    import config
    api_key = config.API_KEY

genai.configure(api_key=api_key)
# --- End of AI Setup ---


DATABASE_NAME = 'fitness_tracker.db'

# --- AI & LOGIC FUNCTIONS ---

def get_nutritional_info(meal_name, quantity):
    """Calls the Gemini API to get an estimate for nutritional information for a given quantity."""
    print(f"🤖 Contacting AI to get nutrition info for '{quantity} of {meal_name}'...")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = f"""Provide a nutritional estimate for the following meal: '{quantity} of {meal_name}'.
        Give me the data in a simple, parsable format like this:
        Calories: 500, Protein: 30g, Carbs: 60g, Fat: 20g
        Only provide this single line of data and nothing else."""
        
        response = model.generate_content(prompt)
        text_response = response.text

        calories = re.search(r"Calories: (\d+)", text_response)
        protein = re.search(r"Protein: (\d+)", text_response)
        carbs = re.search(r"Carbs: (\d+)", text_response)
        fat = re.search(r"Fat: (\d+)", text_response)

        return {
            "calories": int(calories.group(1)) if calories else None,
            "protein": int(protein.group(1)) if protein else None,
            "carbs": int(carbs.group(1)) if carbs else None,
            "fat": int(fat.group(1)) if fat else None,
        }
    except Exception as e:
        print(f"Error contacting AI: {e}")
        return None

def generate_transformation_plan(profile):
    """Generates a transformation plan based on the provided profile data."""
    print("🧠 Generating a transformation plan with user-provided data...")
    
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    prompt1 = f"You are a fitness expert. A client's profile is: {json.dumps(profile)}. Is their goal realistic? Respond only with 'Possible' or 'Impossible' and a one-sentence justification."
    
    try:
        response1 = model.generate_content(prompt1)
        feasibility_response = response1.text.strip().lower()

        shopping_list_instructions = """
        Next, create a 'Weekly Shopping List' section. Consolidate all ingredients from the 7-day meal plan into a categorized list (e.g., Vegetables, Proteins, Grains, etc.).
        For each specific item on the list (e.g., 'Chicken Breast', 'Broccoli', 'Oats'), you MUST provide three unique, clickable Markdown search links for BigBasket, Amazon Fresh, and JioMart.
        Strict Rules:
        1. DO NOT use placeholder phrases like '(links as above)'. Every item needs its own set of three links.
        2. DO NOT include any extra notes, disclaimers, or conversational text at the end. Your response must end after the final link.
        """

        if 'impossible' in feasibility_response:
            prompt2 = f"""
            The client's goal from profile {json.dumps(profile)} is unrealistic. You are a supportive expert.
            Propose a new, safer timeline. Then, generate a 7-day meal plan and a 3-day exercise routine for this new plan, fitting their budget and location.
            {shopping_list_instructions}
            """
        else:
            prompt2 = f"""
            The client's goal from profile {json.dumps(profile)} is achievable. You are their personal trainer.
            Generate a 7-day meal plan and a 3-day exercise routine to help them achieve their goal, fitting their budget and location.
            {shopping_list_instructions}
            """
        
        response2 = model.generate_content(prompt2)
        return response2.text
    except Exception as e:
        return f"❌ An error occurred while generating the plan: {e}"

def log_workout(exercise, sets, reps):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute('INSERT INTO workouts (timestamp, exercise_name, sets, reps) VALUES (?, ?, ?, ?)', 
                   (timestamp, exercise, sets, reps))
    conn.commit()
    conn.close()
    print(f"✅ Logged Workout: {sets} sets of {reps} {exercise}.")

def log_meal(name, quantity):
    ai_data = get_nutritional_info(name, quantity)
    calories, protein, carbs, fat = None, None, None, None
    if ai_data:
        calories = ai_data.get("calories")
        protein = ai_data.get("protein")
        carbs = ai_data.get("carbs")
        fat = ai_data.get("fat")

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute('''
    INSERT INTO meals (timestamp, meal_name, quantity, calories, protein_grams, carbs_grams, fat_grams)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, name, quantity, calories, protein, carbs, fat))
    conn.commit()
    conn.close()
    print(f"✅ Logged Meal: {quantity} of {name}.")

def view_workouts():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, exercise_name, sets, reps FROM workouts ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    
    output = []
    if not rows:
        return ["No workouts logged yet."]
    for row in rows:
        timestamp = datetime.fromisoformat(row[0]).strftime('%Y-%m-%d %H:%M')
        output.append(f"[{timestamp}] {row[1]}: {row[2]} sets of {row[3]} reps")
    return output

def view_meals():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, meal_name, quantity, calories, protein_grams, carbs_grams, fat_grams FROM meals ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    output = []
    if not rows:
        return ["No meals logged yet."]
    for row in rows:
        timestamp = datetime.fromisoformat(row[0]).strftime('%Y-%m-%d %H:%M')
        meal_display = f"{row[2]} of {row[1]}" if row[2] else row[1]
        details = f"Cals: {row[3] or 'N/A'}, Prot: {row[4] or 'N/A'}g, Carbs: {row[5] or 'N/A'}g, Fat: {row[6] or 'N/A'}g"
        output.append(f"[{timestamp}] {meal_display} ({details})")
    return output

# --- MAIN FUNCTION for CLI ---
def main():
    parser = argparse.ArgumentParser(description="Your Personal Fitness Tracker CLI.")
    subparsers = parser.add_subparsers(dest='command', required=True, help="Main commands")
    
    # Log command
    log_parser = subparsers.add_parser('log', help="Log a new workout or meal")
    log_subparsers = log_parser.add_subparsers(dest='log_type', required=True, help="Type of item to log")
    
    workout_parser = log_subparsers.add_parser('workout', help="Log a new workout")
    workout_parser.add_argument('--exercise', type=str, required=True)
    workout_parser.add_argument('--sets', type=int, required=True)
    workout_parser.add_argument('--reps', type=int, required=True)
    
    meal_parser = log_subparsers.add_parser('meal', help="Log a new meal")
    meal_parser.add_argument('--name', type=str, required=True)
    meal_parser.add_argument('--quantity', type=str, required=True, help="Serving size (e.g., '1 bowl')")
    
    # View command
    view_parser = subparsers.add_parser('view', help="View logged workouts or meals")
    view_parser.add_argument('item_type', choices=['workouts', 'meals'])
    
    # Plan command
    plan_parser = subparsers.add_parser('plan', help="Generate a new transformation plan (use web app for full functionality)")
    
    args = parser.parse_args()
    
    if args.command == 'log':
        if args.log_type == 'workout':
            log_workout(args.exercise, args.sets, args.reps)
        elif args.log_type == 'meal':
            log_meal(args.name, args.quantity)
    elif args.command == 'view':
        if args.item_type == 'workouts':
            for line in view_workouts(): print(line)
        elif args.item_type == 'meals':
            for line in view_meals(): print(line)
    elif args.command == 'plan':
        print("This feature requires user profile input. Please use the web app (app.py) to generate a plan.")

if __name__ == '__main__':
    main()