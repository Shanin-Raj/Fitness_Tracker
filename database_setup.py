import sqlite3

# Connect to the database (this will create the file if it doesn't exist)
conn = sqlite3.connect('fitness_tracker.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# --- Create the 'workouts' table ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    exercise_name TEXT NOT NULL,
    sets INTEGER NOT NULL,
    reps INTEGER NOT NULL
)
''')

# --- Create the 'meals' Tzble ---
cursor.execute('''
CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    meal_name TEXT NOT NULL,
    calories INTEGER,
    protein_grams INTEGER,
    carbs_grams INTEGER,
    fat_grams INTEGER
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database 'fitness_tracker.db' and tables created successfully. ")