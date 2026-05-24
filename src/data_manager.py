from datetime import datetime
import sqlite3
import os

class DataManager:
    def __init__(self):
        # Database persistence settings
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bmi_calculator.db")
        self._init_db()
        self._load_data()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enable foreign key support in SQLite
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL
            )
        """)
        
        # Create history table with cascading delete
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        # Seed default data if database is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            default_users = [
                (1, "Emily Vance", 26, "Female"),
                (2, "David Miller", 35, "Male")
            ]
            cursor.executemany("INSERT INTO users (id, name, age, gender) VALUES (?, ?, ?, ?)", default_users)
            
            default_history = [
                (101, 1, "2026-01-10", 68.0, 168.0, 24.1, "Normal"),
                (102, 1, "2026-02-15", 66.5, 168.0, 23.6, "Normal"),
                (103, 1, "2026-03-20", 65.0, 168.0, 23.0, "Normal"),
                (104, 1, "2026-04-25", 63.8, 168.0, 22.6, "Normal"),
                (105, 1, "2026-05-24", 63.0, 168.0, 22.3, "Normal"),
                (201, 2, "2026-02-01", 92.0, 180.0, 28.4, "Overweight"),
                (202, 2, "2026-03-01", 90.5, 180.0, 27.9, "Overweight"),
                (203, 2, "2026-04-01", 89.0, 180.0, 27.5, "Overweight"),
                (204, 2, "2026-05-01", 87.5, 180.0, 27.0, "Overweight")
            ]
            cursor.executemany("INSERT INTO history (id, user_id, date, weight, height, bmi, category) VALUES (?, ?, ?, ?, ?, ?, ?)", default_history)
            
            conn.commit()
            
        conn.close()

    def _load_data(self):
        self.users = {}
        self.history = []
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Load users from database
        cursor.execute("SELECT id, name, age, gender FROM users")
        for row in cursor.fetchall():
            self.users[row["id"]] = {
                "id": row["id"],
                "name": row["name"],
                "age": row["age"],
                "gender": row["gender"]
            }
            
        # Load history from database
        cursor.execute("SELECT id, user_id, date, weight, height, bmi, category FROM history")
        for row in cursor.fetchall():
            self.history.append({
                "id": row["id"],
                "user_id": row["user_id"],
                "date": row["date"],
                "weight": row["weight"],
                "height": row["height"],
                "bmi": row["bmi"],
                "category": row["category"]
            })
            
        conn.close()

    def calculate_bmi(self, weight, height, unit_system):
        """Calculates and returns the BMI score.
        Formula:
        Metric: Weight (kg) / Height (m) ^ 2
        Imperial: (Weight (lbs) * 703) / Height (in) ^ 2
        """
        if height <= 0 or weight <= 0:
            raise ValueError("Height and weight must be positive numbers.")
            
        if unit_system == "Metric":
            height_m = height / 100.0
            return weight / (height_m ** 2)
        else:
            return (weight * 703) / (height ** 2)

    def classify_bmi(self, bmi):
        """Returns classification category, status text, and soothing health advice."""
        if bmi < 18.5:
            return {
                "category": "Underweight",
                "status": "UNDERWEIGHT",
                "advice": "Your BMI indicates you are underweight. Consider speaking with a doctor or nutritionist about healthy weight gain."
            }
        elif bmi < 25.0:
            return {
                "category": "Normal",
                "status": "NORMAL WEIGHT",
                "advice": "Great job! You have a healthy weight. Continue eating balanced meals and staying active to maintain it."
            }
        elif bmi < 30.0:
            return {
                "category": "Overweight",
                "status": "OVERWEIGHT",
                "advice": "Your BMI suggests you are slightly overweight. Simple lifestyle tweaks like regular walking and mindful eating can help."
            }
        else:
            return {
                "category": "Obese",
                "status": "OBESE",
                "advice": "Your BMI falls in the obese range. We recommend consulting a healthcare provider for guidance on safe weight management."
            }

    def add_user(self, name, age, gender):
        """Creates a new user profile and returns the user id."""
        if not name:
            raise ValueError("Name cannot be empty.")
        if age <= 0 or age > 120:
            raise ValueError("Age must be between 1 and 120.")
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, age, gender) VALUES (?, ?, ?)",
            (name, age, gender)
        )
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.users[new_id] = {
            "id": new_id,
            "name": name,
            "age": age,
            "gender": gender
        }
        return new_id

    def delete_user(self, user_id):
        """Deletes user profile and related logs."""
        if user_id not in self.users:
            raise KeyError("User does not exist.")
            
        if len(self.users) <= 1:
            raise ValueError("Cannot delete the only remaining user profile.")
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        
        # Delete user in-memory
        del self.users[user_id]
        
        # Delete related history logs in-memory
        self.history = [r for r in self.history if r["user_id"] != user_id]

    def add_history_record(self, user_id, weight, height, bmi, category, date_str=None):
        """Saves a new calculation log. Normalizes inputs to metric (kg/cm) for DB."""
        if user_id not in self.users:
            raise KeyError("User does not exist.")
            
        if not date_str:
            date_str = datetime.today().strftime("%Y-%m-%d")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO history (user_id, date, weight, height, bmi, category) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, date_str, weight, height, bmi, category)
        )
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()

        new_rec = {
            "id": new_id,
            "user_id": user_id,
            "date": date_str,
            "weight": weight,
            "height": height,
            "bmi": bmi,
            "category": category
        }
        self.history.append(new_rec)
        return new_rec

    def get_user_stats(self, user_id):
        """Computes statistical metrics (Min, Avg, Max) BMI scores for active user."""
        records = [r for r in self.history if r["user_id"] == user_id]
        if not records:
            return {"min": None, "avg": None, "max": None}
            
        bmis = [r["bmi"] for r in records]
        return {
            "min": min(bmis),
            "avg": sum(bmis) / len(bmis),
            "max": max(bmis)
        }

    def get_user_history(self, user_id):
        """Gets chronological history records for active user."""
        return sorted(
            [r for r in self.history if r["user_id"] == user_id],
            key=lambda r: r["date"],
            reverse=True
        )

    def delete_history_record(self, record_id):
        """Deletes a specific history record by its ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM history WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()

        self.history = [r for r in self.history if r["id"] != record_id]

