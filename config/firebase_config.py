# firebase_config.py
import firebase_admin
from firebase_admin import credentials, firestore, auth
import pyrebase # Import the new library

# --- Firebase Admin SDK Configuration (for backend tasks) ---
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    # Check if the app is already initialized to prevent errors
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    print("Firebase Admin connection established.")
except Exception as e:
    print(f"Failed to initialize Firebase Admin SDK: {e}")

# Get a reference to the Firestore database (Admin SDK)
db = firestore.client()
# Reference to the authentication service (Admin SDK)
auth_client = auth


# --- Pyrebase Configuration (for user login/signup) ---
# ACTION: Copy your firebaseConfig keys from the Firebase console here
firebase_config = {
  "apiKey": "AIzaSyDDkYCITn-mihXe7fVefTbk04p0KtGT1wg",
  "authDomain": "shanin-fitness-tracker.firebaseapp.com",
  "projectId": "shanin-fitness-tracker",
  "storageBucket": "shanin-fitness-tracker.firebasestorage.app",
  "messagingSenderId": "943926209146",
  "appId": "1:943926209146:web:ee6625acc4ab28ccdfa9c3",
  "databaseURL": "" # You can leave this empty
}

firebase = pyrebase.initialize_app(firebase_config)
# Reference to the authentication service (Pyrebase)
pyrebase_auth = firebase.auth()