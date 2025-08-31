# app.py (With a full UI form for plan generation)
import streamlit as st
import fitness as ft # Import our refactored fitness.py as ft

st.set_page_config(layout="wide")

st.title("S.H.A.N.I.N. Fitness Tracker 🏋️")

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Log Data", "View Progress", "Generate Plan"])

# --- Page 1: Log Data (Unchanged) ---
if page == "Log Data":
    st.header("Log New Activity")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Log a Workout")
        with st.form(key='workout_form'):
            exercise = st.text_input("Exercise Name")
            sets = st.number_input("Sets", min_value=1, step=1)
            reps = st.number_input("Reps", min_value=1, step=1)
            submit_workout = st.form_submit_button("Log Workout")
            if submit_workout:
                if exercise and sets > 0 and reps > 0:
                    ft.log_workout(exercise, sets, reps)
                    st.success(f"Logged {exercise} successfully!")
                else: st.warning("Please fill in all workout fields.")
    with col2:
        st.subheader("Log a Meal")
        with st.form(key='meal_form'):
            meal = st.text_input("Meal Name")
            st.markdown("_(Leave nutrition fields blank for AI to fill them in)_")
            calories = st.number_input("Calories", min_value=0, step=10, format="%d")
            protein = st.number_input("Protein (g)", min_value=0, step=1, format="%d")
            submit_meal = st.form_submit_button("Log Meal")
            if submit_meal:
                if meal:
                    ft.log_meal(meal, calories, protein, None, None)
                    st.success(f"Logged {meal} successfully!")
                else: st.warning("Please enter a meal name.")

# --- Page 2: View Progress (Unchanged) ---
elif page == "View Progress":
    st.header("View Your Progress")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Workout Log")
        if st.button("Refresh Workout Log"):
            workouts = ft.view_workouts()
            st.text_area("Log", value="\n".join(workouts), height=300)
    with col2:
        st.subheader("Meal Log")
        if st.button("Refresh Meal Log"):
            meals = ft.view_meals()
            st.text_area("Log", value="\n".join(meals), height=300)

# --- Page 3: Generate Plan (UPDATED with Form) ---
elif page == "Generate Plan":
    st.header("Generate a New Transformation Plan")
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
        # Create the profile dictionary from the form inputs
        profile_data = {
            "goal": goal,
            "current_weight_kg": current_weight,
            "target_weight_kg": target_weight,
            "target_timeline_months": timeline,
            "height_cm": height,
            "activity_level": activity_level,
            "diet_preference": diet_preference,
            "weekly_budget_inr": budget,
            "location": location
        }
        
        with st.spinner("🤖 Your AI Dietitian is creating a custom plan for you... This may take a moment."):
            plan = ft.generate_transformation_plan(profile_data)
            st.markdown("---")
            st.subheader("Your Personalized Plan:")
            st.markdown(plan)
            st.success("Plan generated!")