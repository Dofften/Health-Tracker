import tkinter as tk
from tkinter import messagebox, simpledialog
import csv
import os
import hashlib
from datetime import datetime

app_state = {
    "current_user": None,
    "current_frame": None
}

USERS_FILE = 'users.csv'
ACTIVITIES_FILE = 'activities.csv'
NUTRITION_FILE = 'nutrition.csv'
GOALS_FILE = 'goals.csv'

def initialize_csv(file_path, headers):
    if not os.path.exists(file_path):
        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
        except IOError as e:
            messagebox.showerror("File Error", f"Could not create file {file_path}: {e}")


def setup_files():
    initialize_csv(USERS_FILE, ['username', 'password'])
    initialize_csv(ACTIVITIES_FILE, ['username', 'date', 'activity_type', 'duration', 'intensity'])
    initialize_csv(NUTRITION_FILE, ['username', 'date', 'calories', 'protein', 'carbs', 'fats'])
    initialize_csv(GOALS_FILE, ['username', 'target_weight', 'workout_frequency'])


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)


def read_csv(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, mode='r', newline='') as file:
            return list(csv.DictReader(file))
    except (IOError, csv.Error) as e:
        messagebox.showerror("Read Error", f"Could not read from {file_path}: {e}")
        return []


def append_to_csv(file_path, data_row):
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
    records = read_csv(GOALS_FILE)
    updated = False
    new_records = []

    new_goal = {'username': username, 'target_weight': target_weight, 'workout_frequency': workout_frequency}

    for record in records:
        if record.get('username') == username:
            new_records.append(new_goal)
            updated = True
        else:
            new_records.append(record)

    if not updated:
        new_records.append(new_goal)

    try:
        with open(GOALS_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['username', 'target_weight', 'workout_frequency'])
            writer.writeheader()
            writer.writerows(new_records)
        return True
    except IOError as e:
        messagebox.showerror("Update Error", f"Could not update goals: {e}")
        return False

def switch_frame(master, frame_creator, *args):
    if app_state["current_frame"] is not None:
        app_state["current_frame"].destroy()

    app_state["current_frame"] = frame_creator(master, *args)
    app_state["current_frame"].pack(pady=20, padx=20, fill="both", expand=True)

def handle_login(master, username_entry, password_entry):
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showerror("Input Error", "Username and password cannot be empty.")
        return

    users = read_csv(USERS_FILE)
    for user in users:
        if user['username'] == username and verify_password(user['password'], password):
            app_state['current_user'] = username
            switch_frame(master, create_main_menu_frame)
            return

    messagebox.showerror("Login Failed", "Invalid username or password.")

def handle_register(username_entry, password_entry):
    username = username_entry.get()
    password = password_entry.get()

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
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)


def handle_save_activity(master, activity_entry, duration_entry, intensity_entry):
    activity_type = activity_entry.get()
    duration = duration_entry.get()
    intensity = intensity_entry.get()
    date = datetime.now().strftime("%Y-%m-%d")

    if not all([activity_type, duration, intensity]):
        messagebox.showerror("Input Error", "All fields are required.")
        return
    try:
        float(duration)
    except ValueError:
        messagebox.showerror("Input Error", "Duration must be a number.")
        return

    data = {'username': app_state['current_user'], 'date': date, 'activity_type': activity_type, 'duration': duration, 'intensity': intensity}
    if append_to_csv(ACTIVITIES_FILE, data):
        messagebox.showinfo("Success", "Activity logged successfully!")
        switch_frame(master, create_main_menu_frame)

def handle_save_nutrition(master, calories_entry, protein_entry, carbs_entry, fats_entry):
    calories, protein, carbs, fats = calories_entry.get(), protein_entry.get(), carbs_entry.get(), fats_entry.get()
    date = datetime.now().strftime("%Y-%m-%d")

    if not all([calories, protein, carbs, fats]):
        messagebox.showerror("Input Error", "All nutrition fields are required.")
        return
    for value, name in [(calories, "Calories"), (protein, "Protein"), (carbs, "Carbs"), (fats, "Fats")]:
        try:
            float(value)
        except ValueError:
            messagebox.showerror("Input Error", f"{name} must be a valid number.")
            return

    data = {'username': app_state['current_user'], 'date': date, 'calories': calories, 'protein': protein, 'carbs': carbs, 'fats': fats}
    if append_to_csv(NUTRITION_FILE, data):
        messagebox.showinfo("Success", "Nutrition logged successfully!")
        switch_frame(master, create_main_menu_frame)



def handle_save_goals(master, weight_entry, frequency_entry):
    target_weight = weight_entry.get()
    workout_frequency = frequency_entry.get()

    if not target_weight or not workout_frequency:
        messagebox.showerror("Input Error", "Both goal fields are required.")
        return
    try:
        float(target_weight)
        int(workout_frequency)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for goals.")
        return

    if update_goal(app_state['current_user'], target_weight, workout_frequency):
        messagebox.showinfo("Success", "Goals saved successfully!")
        switch_frame(master, create_main_menu_frame)


def handle_logout(master):
    app_state['current_user'] = None
    switch_frame(master, create_login_register_frame)


def create_login_register_frame(master):
    frame = tk.Frame(master)
    tk.Label(frame, text="Username", font=("Helvetica", 12)).pack(pady=5)
    username_entry = tk.Entry(frame, font=("Helvetica", 12))
    username_entry.pack(pady=5, padx=20, fill='x')
    tk.Label(frame, text="Password", font=("Helvetica", 12)).pack(pady=5)
    password_entry = tk.Entry(frame, show="*", font=("Helvetica", 12))
    password_entry.pack(pady=5, padx=20, fill='x')
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=20)
    tk.Button(button_frame, text="Login", command=lambda: handle_login(master, username_entry, password_entry), font=("Helvetica", 12, "bold")).pack(side="left", padx=10)
    tk.Button(button_frame, text="Register", command=lambda: handle_register(username_entry, password_entry), font=("Helvetica", 12, "bold")).pack(side="right", padx=10)
    return frame


def create_main_menu_frame(master):
    frame = tk.Frame(master)
    tk.Label(frame, text=f"Welcome, {app_state['current_user']}!", font=("Helvetica", 16, "bold")).pack(pady=10)
    tk.Button(frame, text="Log Activity", command=lambda: switch_frame(master, create_log_activity_frame), font=("Helvetica", 12)).pack(fill="x", pady=5, padx=20)
    tk.Button(frame, text="Track Nutrition", command=lambda: switch_frame(master, create_track_nutrition_frame), font=("Helvetica", 12)).pack(fill="x", pady=5, padx=20)
    tk.Button(frame, text="View Progress", command=lambda: switch_frame(master, create_view_progress_frame), font=("Helvetica", 12)).pack(fill="x", pady=5, padx=20)
    tk.Button(frame, text="Set Goals", command=lambda: switch_frame(master, create_set_goals_frame), font=("Helvetica", 12)).pack(fill="x", pady=5, padx=20)
    tk.Button(frame, text="Logout", command=lambda: handle_logout(master), font=("Helvetica", 12, "bold"), fg="red").pack(fill="x", pady=10, padx=20)
    return frame



def create_log_activity_frame(master):
    frame = tk.Frame(master)
    tk.Label(frame, text="Log Your Activity", font=("Helvetica", 14, "bold")).pack(pady=10)
    tk.Label(frame, text="Activity Type (e.g., Running):").pack()
    activity_entry = tk.Entry(frame)
    activity_entry.pack(pady=5, padx=20, fill='x')
    tk.Label(frame, text="Duration (minutes):").pack()
    duration_entry = tk.Entry(frame)
    duration_entry.pack(pady=5, padx=20, fill='x')
    tk.Label(frame, text="Intensity (Low, Medium, High):").pack()
    intensity_entry = tk.Entry(frame)
    intensity_entry.pack(pady=5, padx=20, fill='x')
    tk.Button(frame, text="Save Activity", command=lambda: handle_save_activity(master, activity_entry, duration_entry, intensity_entry), font=("Helvetica", 12)).pack(pady=20)
    tk.Button(frame, text="Back to Menu", command=lambda: switch_frame(master, create_main_menu_frame), font=("Helvetica", 10)).pack()
    return frame


def create_track_nutrition_frame(master):
    frame = tk.Frame(master)
    tk.Label(frame, text="Track Your Nutrition", font=("Helvetica", 14, "bold")).pack(pady=10)
    tk.Label(frame, text="Calories:").pack()
    calories_entry = tk.Entry(frame)
    calories_entry.pack(pady=5, padx=20, fill='x')
    tk.Label(frame, text="Protein (g):").pack()
    protein_entry = tk.Entry(frame)
    protein_entry.pack(pady=5, padx=20, fill='x')
    tk.Label(frame, text="Carbohydrates (g):").pack()
    carbs_entry = tk.Entry(frame)
    carbs_entry.pack(pady=5, padx=20, fill='x')
    tk.Label(frame, text="Fats (g):").pack()
    fats_entry = tk.Entry(frame)
    fats_entry.pack(pady=5, padx=20, fill='x')
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=20)
    tk.Button(button_frame, text="Save Nutrition Log", command=lambda: handle_save_nutrition(master, calories_entry, protein_entry, carbs_entry, fats_entry), font=("Helvetica", 12)).pack(side="left", padx=10)
    tk.Button(button_frame, text="Back to Menu", command=lambda: switch_frame(master, create_main_menu_frame), font=("Helvetica", 10)).pack(side="right", padx=10)
    return frame

def create_view_progress_frame(master):
    frame = tk.Frame(master)
    tk.Label(frame, text="Your Progress", font=("Helvetica", 16, "bold")).pack(pady=10)
    progress_text = tk.Text(frame, height=15, width=50, font=("Courier", 11), wrap="word")
    progress_text.pack(pady=10, padx=10, fill="both", expand=True)

    user = app_state['current_user']
    activities = [row for row in read_csv(ACTIVITIES_FILE) if row['username'] == user]
    MET_VALUES = {"low": 3, "medium": 5, "high": 8}
    total_workouts = len(activities)
    total_duration = sum(float(act.get('duration', 0)) for act in activities)
    total_calories_burned = sum((MET_VALUES.get(act.get('intensity', 'medium').lower(), 5) * 3.5 * 70) / 200 * float(act.get('duration', 0)) for act in activities)
    estimated_steps = sum(float(act.get('duration', 0)) * 100 for act in activities if 'run' in act.get('activity_type', '').lower() or 'walk' in act.get('activity_type', '').lower())

    goals = [row for row in read_csv(GOALS_FILE) if row['username'] == user]
    goal_text = "No goals set."
    if goals:
        goal = goals[0]
        goal_text = f"Target Weight: {goal.get('target_weight', 'N/A')} kg\nWeekly Workouts: {goal.get('workout_frequency', 'N/A')}"

    progress_report = (f"Progress Report for: {user}\n"
                       f"----------------------------------\n"
                       f"Total Workouts Logged: {total_workouts}\n"
                       f"Total Duration: {total_duration:.2f} minutes\n"
                       f"Estimated Calories Burned: {total_calories_burned:.2f}\n"
                       f"Estimated Steps: {int(estimated_steps)}\n\n"
                       f"--- Your Goals ---\n{goal_text}")

    progress_text.config(state=tk.NORMAL)
    progress_text.delete('1.0', tk.END)
    progress_text.insert(tk.END, progress_report)
    progress_text.config(state=tk.DISABLED)

    tk.Button(frame, text="Back to Menu", command=lambda: switch_frame(master, create_main_menu_frame), font=("Helvetica", 12)).pack(pady=10)
    return frame


def create_set_goals_frame(master):
    frame = tk.Frame(master)
    tk.Label(frame, text="Set Your Goals", font=("Helvetica", 14, "bold")).pack(pady=10)
    tk.Label(frame, text="Target Weight (kg):").pack()

    weight_entry = tk.Entry(frame)
    weight_entry.pack(pady=5, padx=20, fill='x')
    tk.Label(frame, text="Workout Frequency (per week):").pack()

    frequency_entry = tk.Entry(frame)
    frequency_entry.pack(pady=5, padx=20, fill='x')

    goals = [row for row in read_csv(GOALS_FILE) if row['username'] == app_state['current_user']]
    if goals:
        goal = goals[0]
        weight_entry.insert(0, goal.get('target_weight', ''))
        frequency_entry.insert(0, goal.get('workout_frequency', ''))

    tk.Button(frame, text="Save Goals", command=lambda: handle_save_goals(master, weight_entry, frequency_entry), font=("Helvetica", 12)).pack(pady=20)
    tk.Button(frame, text="Back to Menu", command=lambda: switch_frame(master, create_main_menu_frame), font=("Helvetica", 10)).pack()
    return frame




def main():
    root = tk.Tk()
    root.title("Fitness Tracker")
    root.geometry("400x550")
    root.eval('tk::PlaceWindow . center')
    setup_files()
    switch_frame(root, create_login_register_frame)
    root.mainloop()


if __name__ == "__main__":
    main()
