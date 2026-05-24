from datetime import datetime

class DataManager:
    def __init__(self):
        # In-memory mock database state
        self.users = {
            1: {"id": 1, "name": "Emily Vance", "age": 26, "gender": "Female"},
            2: {"id": 2, "name": "David Miller", "age": 35, "gender": "Male"}
        }
        
        self.history = [
            {"id": 101, "user_id": 1, "date": "2026-01-10", "weight": 68.0, "height": 168.0, "bmi": 24.1, "category": "Normal"},
            {"id": 102, "user_id": 1, "date": "2026-02-15", "weight": 66.5, "height": 168.0, "bmi": 23.6, "category": "Normal"},
            {"id": 103, "user_id": 1, "date": "2026-03-20", "weight": 65.0, "height": 168.0, "bmi": 23.0, "category": "Normal"},
            {"id": 104, "user_id": 1, "date": "2026-04-25", "weight": 63.8, "height": 168.0, "bmi": 22.6, "category": "Normal"},
            {"id": 105, "user_id": 1, "date": "2026-05-24", "weight": 63.0, "height": 168.0, "bmi": 22.3, "category": "Normal"},
            
            {"id": 201, "user_id": 2, "date": "2026-02-01", "weight": 92.0, "height": 180.0, "bmi": 28.4, "category": "Overweight"},
            {"id": 202, "user_id": 2, "date": "2026-03-01", "weight": 90.5, "height": 180.0, "bmi": 27.9, "category": "Overweight"},
            {"id": 203, "user_id": 2, "date": "2026-04-01", "weight": 89.0, "height": 180.0, "bmi": 27.5, "category": "Overweight"},
            {"id": 204, "user_id": 2, "date": "2026-05-01", "weight": 87.5, "height": 180.0, "bmi": 27.0, "category": "Overweight"},
        ]
        
        self.next_user_id = 3
        self.next_history_id = 301

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
            
        new_id = self.next_user_id
        self.next_user_id += 1
        
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
            
        # Delete user
        del self.users[user_id]
        
        # Delete related history logs
        self.history = [r for r in self.history if r["user_id"] != user_id]

    def add_history_record(self, user_id, weight, height, bmi, category, date_str=None):
        """Saves a new calculation log. Normalizes inputs to metric (kg/cm) for DB."""
        if user_id not in self.users:
            raise KeyError("User does not exist.")
            
        if not date_str:
            date_str = datetime.today().strftime("%Y-%m-%d")

        new_rec = {
            "id": self.next_history_id,
            "user_id": user_id,
            "date": date_str,
            "weight": weight,
            "height": height,
            "bmi": bmi,
            "category": category
        }
        
        self.next_history_id += 1
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
        self.history = [r for r in self.history if r["id"] != record_id]

