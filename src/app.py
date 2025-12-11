# app.py (Version 3 with Authentication)
import streamlit as st
import src.fitness as ft
import src.auth_functions as auth
import re

st.set_page_config(layout="wide")

# Initialize session state for user authentication
if 'user' not in st.session_state:
    st.session_state.user = None

# --- Main App Logic ---

# If user is not logged in, show the login/signup page
if st.session_state.user is None:
    st.title("Welcome to the AI Fitness Tracker")
    
    choice = st.selectbox("Login / Signup", ["Login", "Sign Up"])

    if choice == "Login":
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user_info = auth.login(email, password)
            if user_info:
                st.session_state.user = user_info
                st.rerun() # Rerun the app to show the main content

    else:
        st.subheader("Create a New Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            auth.sign_up(email, password)

# If user is logged in, show the main application
else:
    st.title("AI Fitness Tracker 🏋️")

    # --- Sidebar Navigation ---
    st.sidebar.title(f"Welcome!")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
    
    page = st.sidebar.radio("Go to", ["Log Data", "View Progress", "Generate Plan"])

    # --- Page 1: Log Data ---
    if page == "Log Data":
        st.header("Log New Activity")
        # The rest of your Log Data page code goes here...
        col1, col2 = st.columns(2)
        # In app.py, replace the "Log a Workout" section

        with col1:
            st.subheader("Log a Workout")
            with st.form(key='workout_form'):
                exercise = st.text_input("Exercise Name")
                sets = st.number_input("Sets", min_value=1, step=1)
                reps = st.number_input("Reps", min_value=1, step=1)
                submit_workout = st.form_submit_button("Log Workout")
                
                if submit_workout:
                    if exercise and sets > 0 and reps > 0:
                        # UPDATED LINE: Pass the logged-in user's ID
                        user_id = st.session_state.user['localId']
                        ft.log_workout(user_id, exercise, sets, reps)
                        st.success(f"Logged {exercise} successfully!")
                    else:
                        st.warning("Please fill in all workout fields.")
        with col2:
            st.subheader("Log a Meal")
            with st.form(key='meal_form'):
                meal = st.text_input("Meal Name", placeholder="e.g., Chicken Curry")
                quantity = st.text_input("Quantity / Serving Size", placeholder="e.g., 1 bowl, 200g, 4 pieces")
                submit_meal = st.form_submit_button("Log Meal")
                if submit_meal:
                    if meal and quantity:
                        ft.log_meal(meal, quantity)
                        st.success(f"Logged {quantity} of {meal} successfully!")
                    else: st.warning("Please enter both a meal name and a quantity.")

    # --- Page 2: View Progress ---
    elif page == "View Progress":
        st.header("View Your Progress")
        # The rest of your View Progress page code goes here...
        col1, col2 = st.columns(2)
       # In app.py, update the "Workout Log" section inside "View Progress"

        with col1:
            st.subheader("Workout Log")
            # UPDATED: Pass the user_id to the view function
            user_id = st.session_state.user['localId']
            workouts = ft.view_workouts(user_id)
            st.text_area("Log", value="\n".join(workouts), height=300, key="workout_log_area")
        with col2:
            st.subheader("Meal Log")
            meals = ft.view_meals()
            st.text_area("Log", value="\n".join(meals), height=300, key="meal_log_area")

    # --- Page 3: Generate Plan ---
    elif page == "Generate Plan":
        st.header("Generate a New Transformation Plan")
        # The rest of your Generate Plan page code goes here...
        st.info("Fill in your details below to get a personalized meal and exercise plan from the AI.")
        with st.form(key='profile_form'):
            st.subheader("Your Profile")
            col1, col2, col3 = st.columns(3)
            with col1:
                goal = st.selectbox("Main Goal", ["Weight Loss", "Muscle Gain", "General Fitness"])
                current_weight = st.number_input("Current Weight (kg)", min_value=30.0, step=0.5, format="%.1f")
                target_weight = st.number_input("Target Weight (kg)", min_value=30.0, step=0.5, format="%.1f")
            with col2:
                height = st.number_input("Height (cm)", min_value=100, step=1)
                timeline = st.number_input("Target Timeline (months)", min_value=1, step=1)
                budget = st.number_input("Weekly Budget (INR)", min_value=500, step=100)
            with col3:
                activity_level = st.selectbox("Activity Level", ["Sedentary (office job)", "Lightly Active", "Moderately Active", "Very Active"])
                diet_preference = st.selectbox("Diet Preference", ["Anything", "Non-vegetarian", "Vegetarian", "Vegan"])
                location = st.text_input("Your Location (e.g., city, state)", "Kannur, Kerala, India")
            submit_button = st.form_submit_button("✨ Generate My Plan")
        if submit_button:
            profile_data = {
                "goal": goal, "current_weight_kg": current_weight, "target_weight_kg": target_weight,
                "target_timeline_months": timeline, "height_cm": height, "activity_level": activity_level,
                "diet_preference": diet_preference, "weekly_budget_inr": budget, "location": location
            }
            with st.spinner("🤖 Your AI Dietitian is creating a custom plan for you... This may take a moment."):
                full_plan_text = ft.generate_transformation_plan(profile_data)
                st.markdown("---")
                st.subheader("Your Personalized Plan:")
                plan_parts = re.split(r'#+\s*Weekly Shopping List', full_plan_text, flags=re.IGNORECASE)
                main_plan = plan_parts[0]
                st.markdown(main_plan)
                if len(plan_parts) > 1:
                    shopping_list = plan_parts[1]
                    with st.expander("🛒 View Your Weekly Shopping List & Purchase Links"):
                        st.markdown(shopping_list)
                st.success("Plan generated!")