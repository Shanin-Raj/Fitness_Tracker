import json
from app import app, db, FoodItem

def seed_data():
    with app.app_context():
        # 1. Create the new table if it doesn't exist
        db.create_all()
        
        # 2. Check if we already have food to avoid duplicates
        if FoodItem.query.first():
            print("⚠️  Database already has food! Skipping seed.")
            return

        # 3. Load the JSON file
        print("⏳ Loading food data...")
        with open('data/kerala_food.json', 'r') as f:
            data = json.load(f)

        # 4. Loop through the list and add to DB
        for item in data:
            food = FoodItem(
                name=item['name'],
                calories=item['calories'],
                protein=item['protein'],
                carbs=item['carbs'],
                fats=item['fats']
            )
            db.session.add(food)
        
        # 5. Save everything
        db.session.commit()
        print("✅ Success! Added 10 Kerala food items to the database.")

if __name__ == "__main__":
    seed_data()