import tkinter as tk
from tkinter import messagebox, simpledialog
import csv
import os
import hashlib
from datetime import datetime

# file paths for data storage
USERS_FILE = 'users.csv'
ACTIVITIES_FILE = 'activities.csv'
NUTRITION_FILE = 'nutrition.csv'
GOALS_FILE = 'goals.csv'


# --- File Handling and Initialization ---

def initialize_csv(file_path, headers):
    """Initializes a CSV file with headers if it doesn't exist."""
    if not os.path.exists(file_path):
        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
        except IOError as e:
            messagebox.showerror("File Error", f"Could not create file {file_path}: {e}")


def setup_files():
    """Ensure all required CSV files are created."""
    initialize_csv(USERS_FILE, ['username', 'password'])
    initialize_csv(ACTIVITIES_FILE, ['username', 'date', 'activity_type', 'duration', 'intensity'])
    initialize_csv(NUTRITION_FILE, ['username', 'date', 'calories', 'protein', 'carbs', 'fats'])
    initialize_csv(GOALS_FILE, ['username', 'target_weight', 'workout_frequency'])


# --- Utility Functions ---

def hash_password(password):
    """Hashes a password for secure storage."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(stored_password, provided_password):
    """Verifies a provided password against a stored hash."""
    return stored_password == hash_password(provided_password)


# --- Data Handling Functions ---

def read_csv(file_path):
    """Reads all rows from a CSV file."""
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, mode='r', newline='') as file:
            return list(csv.DictReader(file))
    except (IOError, csv.Error) as e:
        messagebox.showerror("Read Error", f"Could not read from {file_path}: {e}")
        return []


def append_to_csv(file_path, data_row):
    """Appends a new row of data to a CSV file."""
    try:
        file_exists = os.path.exists(file_path)
        with open(file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data_row.keys())
            if not file_exists or file.tell() == 0:
                writer.writeheader()
            writer.writerow(data_row)
        return True
    except IOError as e:
        messagebox.showerror("Write Error", f"Could not write to {file_path}: {e}")
        return False


def update_goal(username, target_weight, workout_frequency):
    """Updates or adds a goal for a specific user."""
    records = read_csv(GOALS_FILE)
    updated = False
    new_records = []

    # Create the new goal entry
    new_goal = {'username': username, 'target_weight': target_weight, 'workout_frequency': workout_frequency}

    # Find if a goal for the user already exists and update it
    for record in records:
        if record.get('username') == username:
            new_records.append(new_goal)
            updated = True
        else:
            new_records.append(record)

    # If no goal was found for the user, add the new one
    if not updated:
        new_records.append(new_goal)

    # Write all records back to the file
    try:
        with open(GOALS_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['username', 'target_weight', 'workout_frequency'])
            writer.writeheader()
            writer.writerows(new_records)
        return True
    except IOError as e:
        messagebox.showerror("Update Error", f"Could not update goals: {e}")
        return False


# --- Main Application Class ---

class FitnessTrackerApp(tk.Tk):
    """The main application window and logic."""

    def __init__(self):
        super().__init__()
        self.title("Fitness Tracker")
        self.geometry("400x400")

        # Ensures all data files are ready before starting
        setup_files()

        self.current_user = None

        # Container frame for switching between different screens
        self._frame = None
        self.switch_frame(LoginRegisterFrame)

    def switch_frame(self, frame_class, *args):
        """Destroys the current frame and replaces it with a new one."""
        if self._frame is not None:
            self._frame.destroy()
        self._frame = frame_class(self, *args)
        self._frame.pack(pady=20, padx=20, fill="both", expand=True)


# --- GUI Frames ---

class LoginRegisterFrame(tk.Frame):
    """Frame for user login and registration."""

    def __init__(self, master):
        super().__init__(master)
        self.master = master

        tk.Label(self, text="Username", font=("Helvetica", 12)).pack(pady=5)
        self.username_entry = tk.Entry(self, font=("Helvetica", 12))
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password", font=("Helvetica", 12)).pack(pady=5)
        self.password_entry = tk.Entry(self, show="*", font=("Helvetica", 12))
        self.password_entry.pack(pady=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Login", command=self.login, font=("Helvetica", 12, "bold")).pack(side="left",
                                                                                                       padx=10)
        tk.Button(button_frame, text="Register", command=self.register, font=("Helvetica", 12, "bold")).pack(
            side="right", padx=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Input Error", "Username and password cannot be empty.")
            return

        users = read_csv(USERS_FILE)
        user_found = False
        for user in users:
            if user['username'] == username and verify_password(user['password'], password):
                self.master.current_user = username
                self.master.switch_frame(MainMenuFrame)
                user_found = True
                break

        if not user_found:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Input Error", "Username and password cannot be empty.")
            return

        users = read_csv(USERS_FILE)
        if any(user['username'] == username for user in users):
            messagebox.showerror("Registration Failed", "Username already exists.")
            return

        hashed_pwd = hash_password(password)
        if append_to_csv(USERS_FILE, {'username': username, 'password': hashed_pwd}):
            messagebox.showinfo("Success", "Registration successful! You can now log in.")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)


class MainMenuFrame(tk.Frame):
    """The main menu displayed after a successful login."""

    def __init__(self, master):
        super().__init__(master)
        self.master = master

        tk.Label(self, text=f"Welcome, {self.master.current_user}!", font=("Helvetica", 16, "bold")).pack(pady=10)

        tk.Button(self, text="Log Activity", command=self.log_activity, font=("Helvetica", 12)).pack(fill="x", pady=5)
        tk.Button(self, text="Track Nutrition", command=self.track_nutrition, font=("Helvetica", 12)).pack(fill="x",
                                                                                                           pady=5)
        tk.Button(self, text="View Progress", command=self.view_progress, font=("Helvetica", 12)).pack(fill="x", pady=5)
        tk.Button(self, text="Set Goals", command=self.set_goals, font=("Helvetica", 12)).pack(fill="x", pady=5)
        tk.Button(self, text="Logout", command=self.logout, font=("Helvetica", 12, "bold"), fg="red").pack(fill="x",
                                                                                                           pady=10)

    def log_activity(self):
        self.master.switch_frame(LogActivityFrame)

    def track_nutrition(self):
        self.master.switch_frame(TrackNutritionFrame)

    def view_progress(self):
        self.master.switch_frame(ViewProgressFrame)

    def set_goals(self):
        self.master.switch_frame(SetGoalsFrame)

    def logout(self):
        self.master.current_user = None
        self.master.switch_frame(LoginRegisterFrame)


class LogActivityFrame(tk.Frame):
    """Frame for logging a new activity."""

    def __init__(self, master):
        super().__init__(master)
        self.master = master

        tk.Label(self, text="Log Your Activity", font=("Helvetica", 14, "bold")).pack(pady=10)

        tk.Label(self, text="Activity Type (e.g., Running):").pack()
        self.activity_type_entry = tk.Entry(self)
        self.activity_type_entry.pack(pady=5)

        tk.Label(self, text="Duration (minutes):").pack()
        self.duration_entry = tk.Entry(self)
        self.duration_entry.pack(pady=5)

        tk.Label(self, text="Intensity (Low, Medium, High):").pack()
        self.intensity_entry = tk.Entry(self)
        self.intensity_entry.pack(pady=5)

        tk.Button(self, text="Save Activity", command=self.save_activity, font=("Helvetica", 12)).pack(pady=20)
        tk.Button(self, text="Back to Menu", command=lambda: self.master.switch_frame(MainMenuFrame), font=("Helvetica", 10)).pack()

    def save_activity(self):
        activity_type = self.activity_type_entry.get()
        duration = self.duration_entry.get()
        intensity = self.intensity_entry.get()
        date = datetime.now().strftime("%Y-%m-%d")

        if not all([activity_type, duration, intensity]):
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            # Validate duration is a number
            float(duration)
        except ValueError:
            messagebox.showerror("Input Error", "Duration must be a number.")
            return

        data = {
            'username': self.master.current_user,
            'date': date,
            'activity_type': activity_type,
            'duration': duration,
            'intensity': intensity
        }

        if append_to_csv(ACTIVITIES_FILE, data):
            messagebox.showinfo("Success", "Activity logged successfully!")
            self.master.switch_frame(MainMenuFrame)
        else:
            messagebox.showerror("Error", "Failed to log activity.")


class TrackNutritionFrame(tk.Frame):
    """Frame for tracking daily nutritional intake."""

    def __init__(self, master):
        super().__init__(master)
        self.master = master

        tk.Label(self, text="Track Your Nutrition", font=("Helvetica", 14, "bold")).pack(pady=10)

        tk.Label(self, text="Calories:").pack()
        self.calories_entry = tk.Entry(self)
        self.calories_entry.pack(pady=5)

        tk.Label(self, text="Protein (g):").pack()
        self.protein_entry = tk.Entry(self)
        self.protein_entry.pack(pady=5)

        tk.Label(self, text="Carbohydrates (g):").pack()
        self.carbs_entry = tk.Entry(self)
        self.carbs_entry.pack(pady=5)

        tk.Label(self, text="Fats (g):").pack()
        self.fats_entry = tk.Entry(self)
        self.fats_entry.pack(pady=5)

        # Create a dedicated frame for buttons to ensure proper layout
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Save Nutrition Log", command=self.save_nutrition, font=("Helvetica", 12)).pack(
            side="left", padx=10)
        tk.Button(button_frame, text="Back to Menu", command=lambda: self.master.switch_frame(MainMenuFrame),
                  font=("Helvetica", 10)).pack(side="right", padx=10)

    def save_nutrition(self):
        calories = self.calories_entry.get()
        protein = self.protein_entry.get()
        carbs = self.carbs_entry.get()
        fats = self.fats_entry.get()
        date = datetime.now().strftime("%Y-%m-%d")

        if not all([calories, protein, carbs, fats]):
            messagebox.showerror("Input Error", "All fields are required.")
            return

        # Validate that inputs are numbers
        for value, name in [(calories, "Calories"), (protein, "Protein"), (carbs, "Carbs"), (fats, "Fats")]:
            try:
                float(value)
            except ValueError:
                messagebox.showerror("Input Error", f"{name} must be a number.")
                return

        data = {
            'username': self.master.current_user,
            'date': date,
            'calories': calories,
            'protein': protein,
            'carbs': carbs,
            'fats': fats
        }

        if append_to_csv(NUTRITION_FILE, data):
            messagebox.showinfo("Success", "Nutrition logged successfully!")
            self.master.switch_frame(MainMenuFrame)
        else:
            messagebox.showerror("Error", "Failed to log nutrition.")


class ViewProgressFrame(tk.Frame):
    """Frame for viewing user's progress."""

    def __init__(self, master):
        super().__init__(master)
        self.master = master

        tk.Label(self, text="Your Progress", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.progress_text = tk.Text(self, height=10, width=50, font=("Courier", 11))
        self.progress_text.pack(pady=10)
        self.progress_text.config(state=tk.DISABLED)  # Make it read-only

        self.load_progress()

        tk.Button(self, text="Back to Menu", command=lambda: self.master.switch_frame(MainMenuFrame),
                  font=("Helvetica", 12)).pack(pady=10)

    def load_progress(self):
        user = self.master.current_user
        activities = [row for row in read_csv(ACTIVITIES_FILE) if row['username'] == user]

        # MET (Metabolic Equivalent of Task) values for calorie estimation
        MET_VALUES = {"low": 3, "medium": 5, "high": 8}

        total_workouts = len(activities)
        total_duration = sum(float(act['duration']) for act in activities)

        # Estimate calories burned
        total_calories_burned = 0
        for act in activities:
            intensity = act.get('intensity', 'medium').lower()
            met = MET_VALUES.get(intensity, 5)  # Default to medium if intensity is unknown
            duration_min = float(act.get('duration', 0))
            # Formula: (MET * 3.5 * Body Weight in kg) / 200 * duration_in_minutes
            # We assume a default body weight of 70kg for this simple estimation
            calories_burned = (met * 3.5 * 70) / 200 * duration_min
            total_calories_burned += calories_burned

        # Estimate steps (very rough estimation)
        # Assume 100 steps per minute for walking/running activities
        estimated_steps = 0
        for act in activities:
            if 'run' in act['activity_type'].lower() or 'walk' in act['activity_type'].lower():
                estimated_steps += float(act['duration']) * 100

        # Get goals
        goals = [row for row in read_csv(GOALS_FILE) if row['username'] == user]
        goal_text = "No goals set."
        if goals:
            goal = goals[0]
            goal_text = f"Target Weight: {goal['target_weight']} kg\nWeekly Workouts: {goal['workout_frequency']}"

        progress_report = (
            f"Progress Report for: {user}\n"
            f"----------------------------------\n"
            f"Total Workouts Logged: {total_workouts}\n"
            f"Total Duration: {total_duration:.2f} minutes\n"
            f"Estimated Calories Burned: {total_calories_burned:.2f}\n"
            f"Estimated Steps: {int(estimated_steps)}\n\n"
            f"--- Your Goals ---\n"
            f"{goal_text}"
        )

        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.delete('1.0', tk.END)
        self.progress_text.insert(tk.END, progress_report)
        self.progress_text.config(state=tk.DISABLED)


class SetGoalsFrame(tk.Frame):
    """Frame for setting user goals."""

    def __init__(self, master):
        super().__init__(master)
        self.master = master

        tk.Label(self, text="Set Your Goals", font=("Helvetica", 14, "bold")).pack(pady=10)

        tk.Label(self, text="Target Weight (kg):").pack()
        self.weight_entry = tk.Entry(self)
        self.weight_entry.pack(pady=5)

        tk.Label(self, text="Workout Frequency (per week):").pack()
        self.frequency_entry = tk.Entry(self)
        self.frequency_entry.pack(pady=5)

        self.load_existing_goals()

        tk.Button(self, text="Save Goals", command=self.save_goals, font=("Helvetica", 12)).pack(pady=20)
        tk.Button(self, text="Back to Menu", command=lambda: self.master.switch_frame(MainMenuFrame),
                  font=("Helvetica", 10)).pack()

    def load_existing_goals(self):
        """Loads and displays the user's current goals if they exist."""
        goals = [row for row in read_csv(GOALS_FILE) if row['username'] == self.master.current_user]
        if goals:
            goal = goals[0]
            self.weight_entry.insert(0, goal.get('target_weight', ''))
            self.frequency_entry.insert(0, goal.get('workout_frequency', ''))

    def save_goals(self):
        target_weight = self.weight_entry.get()
        workout_frequency = self.frequency_entry.get()

        if not target_weight or not workout_frequency:
            messagebox.showerror("Input Error", "Both fields are required.")
            return

        try:
            float(target_weight)
            int(workout_frequency)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for goals.")
            return

        if update_goal(self.master.current_user, target_weight, workout_frequency):
            messagebox.showinfo("Success", "Goals saved successfully!")
            self.master.switch_frame(MainMenuFrame)
        else:
            messagebox.showerror("Error", "Failed to save goals.")


if __name__ == "__main__":
    app = FitnessTrackerApp()
    app.mainloop()
