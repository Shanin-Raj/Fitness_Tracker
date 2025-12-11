# auth_functions.py
from config.firebase_config import pyrebase_auth
import streamlit as st

def sign_up(email, password):
    """Signs up a new user with email and password."""
    try:
        user = pyrebase_auth.create_user_with_email_and_password(email, password)
        st.success("Account created successfully! Please log in.")
        return True
    except Exception as e:
        # Firebase returns errors in a specific JSON format
        error_message = e.args[1]
        st.error(f"Failed to create account: {error_message}")
        return False

def login(email, password):
    """Logs in an existing user."""
    try:
        user = pyrebase_auth.sign_in_with_email_and_password(email, password)
        st.success("Logged in successfully!")
        return user # Return user info on success
    except Exception as e:
        error_message = e.args[1]
        st.error(f"Login failed: {error_message}")
        return None