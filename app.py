import os
import json
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from groq import Groq
from datetime import datetime,date

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- CONFIG ---
app.config['SECRET_KEY'] = 'secretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# --- AI SETUP (Groq) ---
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- MODELS ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fats = db.Column(db.Float, nullable=False)

class FoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0) # How many servings?
    total_calories = db.Column(db.Integer, nullable=False)
    total_protein = db.Column(db.Float, nullable=False)
    total_carbs = db.Column(db.Float, nullable=False)
    total_fats = db.Column(db.Float, nullable=False)
    date_eaten = db.Column(db.DateTime, default=datetime.utcnow) # Timestamp

# --- HELPER FUNCTION: ASK AI ---
def get_food_info_from_ai(food_name):
    """Asks Groq AI for food macros and returns a Python Dictionary"""
    prompt = f"""
    You are a nutritionist expert in Indian and Kerala cuisine.
    I need nutritional info for: "{food_name}".
    Return ONLY a valid JSON object with standard values for 1 serving (approx 100g or 1 piece).
    Format:
    {{
        "name": "Standardized Name",
        "calories": integer,
        "protein": float (grams),
        "carbs": float (grams),
        "fats": float (grams)
    }}
    Do not add any markdown formatting like ```json. Just raw JSON text.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        clean_text = response.choices[0].message.content.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"AI Error: {e}")
        return None

# --- ROUTES ---

@app.route('/')
def home():
    if current_user.is_authenticated:
        # 1. Get logs for ONLY today (from midnight onwards)
        today_start = datetime.combine(date.today(), datetime.min.time())
        
        logs = FoodLog.query.filter_by(user_id=current_user.id)\
                .filter(FoodLog.date_eaten >= today_start)\
                .all()
        
        # 2. Calculate Totals (Python Math)
        totals = {
            "calories": sum(log.total_calories for log in logs),
            "protein": sum(log.total_protein for log in logs),
            "carbs": sum(log.total_carbs for log in logs),
            "fats": sum(log.total_fats for log in logs)
        }
        
        return render_template('dashboard.html', user=current_user, logs=logs, totals=totals)
    else:
        return render_template('index.html')
    
# --- NEW: AI COACH ROUTE ---
@app.route('/ask_ai', methods=['POST'])
@login_required
def ask_ai():
    user_message = request.json.get('message')
    
    # 1. Define the Persona (The "System Prompt")
    system_instruction = """You are 'Chettan', a friendly and knowledgeable fitness coach from Kerala. 
You help people with Indian/Kerala diet tips, workout advice, and motivation.
- Keep answers short (under 3 sentences).
- Use simple English.
- If asked about non-fitness topics (like math or coding), politely refuse.
- Be encouraging!"""
    
    try:
        # 2. Ask Groq
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=150
        )
        ai_reply = response.choices[0].message.content.strip()
        return jsonify({"reply": ai_reply})
    except Exception as e:
        print(f"AI Coach Error: {e}")
        return jsonify({"reply": "Sorry, I am taking a rest break. Try again later!"})


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
        except:
            flash("Username or Email already exists!")
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/add_log', methods=['POST'])
@login_required
def add_log():
    data = request.json # Get data sent from JavaScript
    
    new_log = FoodLog(
        user_id=current_user.id,
        food_name=data['name'],
        quantity=float(data['quantity']),
        total_calories=int(data['calories']),
        total_protein=float(data['protein']),
        total_carbs=float(data['carbs']),
        total_fats=float(data['fats'])
    )
    
    db.session.add(new_log)
    db.session.commit()
    
    return jsonify({"message": "Added successfully!"})

# --- NEW: THE HYBRID SEARCH ROUTE ---
@app.route('/search_food')
@login_required
def search_food():
    query = request.args.get('query') # Get the search term from URL
    if not query:
        return jsonify([])

    # 1. Check Local Database First (Fast!)
    # We use ILIKE logic (case insensitive) for better matching
    existing_food = FoodItem.query.filter(FoodItem.name.ilike(f"%{query}%")).first()
    
    if existing_food:
        print(f"✅ Found '{query}' in Database!")
        return jsonify({
            "name": existing_food.name,
            "calories": existing_food.calories,
            "protein": existing_food.protein,
            "carbs": existing_food.carbs,
            "fats": existing_food.fats,
            "source": "database"
        })

    # 2. If not found, ask AI (Smart!)
    print(f"🤖 Database missing '{query}'. Asking Gemini...")
    ai_data = get_food_info_from_ai(query)

    if ai_data:
        # 3. Save AI result to Database so we never ask again (Caching)
        new_food = FoodItem(
            name=ai_data['name'],
            calories=ai_data['calories'],
            protein=ai_data['protein'],
            carbs=ai_data['carbs'],
            fats=ai_data['fats']
        )
        db.session.add(new_food)
        db.session.commit()
        
        # Add a "source" tag so we know it came from AI
        ai_data['source'] = "ai_generated"
        return jsonify(ai_data)

    return jsonify({"error": "Food not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)