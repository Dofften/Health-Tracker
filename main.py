import tkinter as tk
import csv
import os
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
        except:
            print("File Error")


def setupFiles():
    initialize_csv(USERS_FILE, ['username', 'password'])
    initialize_csv(ACTIVITIES_FILE, ['username', 'date', 'activity_type', 'duration', 'intensity'])
    initialize_csv(NUTRITION_FILE, ['username', 'date', 'calories', 'protein', 'carbs', 'fats'])
    initialize_csv(GOALS_FILE, ['username', 'target_weight', 'workout_frequency'])


def read_csv(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, mode='r', newline='') as file:
            return list(csv.DictReader(file))
    except:
        print("could not read file")
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
    except:
        print(" could not write to file")
        return False


def updateGoal(username, target_weight, workout_frequency):
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
    except:
        print("Could not update goals")
        return False

def switch_frame(master, frame_creator, *args):
    if app_state["current_frame"] is not None:
        app_state["current_frame"].destroy()

    app_state["current_frame"] = frame_creator(master, *args)
    app_state["current_frame"].pack(pady=20, padx=20, fill="both", expand=True)

def login(master, username_entry, password_entry):
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        print("Please inout username and password.")
        return

    users = read_csv(USERS_FILE)
    for user in users:
        if user['username'] == username and user['password'] == password:
            app_state['current_user'] = username
            switch_frame(master, main_menu)
            return
    print("Invalid username or password.")

def register(username_entry, password_entry):
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        print("Please inout username and password.")
        return

    users = read_csv(USERS_FILE)
    for user in users:
        if user['username'] == username:
            print("Username already exists.")
            return

    if append_to_csv(USERS_FILE, {'username': username, 'password': password}):
        print("Registration successful")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)


def saveActivity(master, activity_entry, duration_entry, intensity_entry, weight_entry):
    activity_type = activity_entry.get()
    duration = duration_entry.get()
    intensity = intensity_entry.get()
    weight = weight_entry.get()
    date = datetime.now().strftime("%Y-%m-%d")

    if activity_type == "" or duration == "" or intensity == "" or weight == "":
        print("All fields are required.")
        return
    try:
        float(duration)
    except:
        print("Duration must be a number.")
        return

    data = {'username': app_state['current_user'], 'date': date, 'activity_type': activity_type, 'duration': duration, 'intensity': intensity, 'weight': weight}
    if append_to_csv(ACTIVITIES_FILE, data):
        print("Activity logged successfully!")
        switch_frame(master, main_menu)

def saveNutrition(master, calories_entry, protein_entry, carbs_entry, fats_entry):
    calories, protein, carbs, fats = calories_entry.get(), protein_entry.get(), carbs_entry.get(), fats_entry.get()
    date = datetime.now().strftime("%Y-%m-%d")


    if calories == "" or protein == "" or carbs == "" or fats == "":
        print("All nutrition fields are required.")
        return
    
    for value, name in [(calories, "Calories"), (protein, "Protein"), (carbs, "Carbs"), (fats, "Fats")]:
        try:
            float(value)
        except:
            print(f"{name} must be a valid number.")
            return


    data = {'username': app_state['current_user'], 'date': date, 'calories': calories, 'protein': protein, 'carbs': carbs, 'fats': fats}
    if append_to_csv(NUTRITION_FILE, data):
        print("Nutrition logged successfully!")
        switch_frame(master, main_menu)



def saveGoal(master, weight_entry, frequency_entry):
    target_weight = weight_entry.get()
    workout_frequency = frequency_entry.get()

    if not target_weight or not workout_frequency:
        print("Both goal fields are required.")
        return
    try:
        float(target_weight)
        int(workout_frequency)
    except:
        print("Please enter valid numbers for goals.")
        return

    if updateGoal(app_state['current_user'], target_weight, workout_frequency):
        print("Goals saved successfully!")
        switch_frame(master, main_menu)


def logout(master):
    app_state['current_user'] = None
    switch_frame(master, login_register_page)


def login_register_page(master):
    frame = tk.Frame(master)
    
    tk.Label(frame, text="Username", font=("Helvetica", 12)).pack(pady=5)
    username_entry = tk.Entry(frame, font=("Helvetica", 12))
    username_entry.pack(pady=5, padx=20, fill='x')
    
    tk.Label(frame, text="Password", font=("Helvetica", 12)).pack(pady=5)
    password_entry = tk.Entry(frame, show="*", font=("Helvetica", 12))
    password_entry.pack(pady=5, padx=20, fill='x')
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="Login", command=lambda: login(master, username_entry, password_entry), font=("Helvetica", 12, "bold")).pack(side="left", padx=10)
    tk.Button(button_frame, text="Register", command=lambda: register(username_entry, password_entry), font=("Helvetica", 12, "bold")).pack(side="right", padx=10)
    return frame


def main_menu(master):
    frame = tk.Frame(master)
    
    tk.Label(frame, text=f"Welcome, {app_state['current_user']}!", font=("Helvetica", 16, "bold")).pack(pady=10)
    tk.Button(frame, text="Log Activity", command=lambda: switch_frame(master, log_activity_page), font=("Helvetica", 12)).pack(fill="x", pady=5, padx=20)
    tk.Button(frame, text="Track Nutrition", command=lambda: switch_frame(master, track_nutrition_page), font=("Helvetica", 12)).pack(fill="x", pady=5, padx=20)
    tk.Button(frame, text="View Progress", command=lambda: switch_frame(master, progress_page), font=("Helvetica", 12)).pack(fill="x", pady=5, padx=20)
    tk.Button(frame, text="Set Goals", command=lambda: switch_frame(master, set_goal_page), font=("Helvetica", 12)).pack(fill="x", pady=5, padx=20)
    tk.Button(frame, text="Logout", command=lambda: logout(master), font=("Helvetica", 12, "bold")).pack(fill="x", pady=10, padx=20)
    
    return frame



def log_activity_page(master):
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

    tk.Label(frame, text="Weight(in kgs):").pack()
    weight_entry = tk.Entry(frame)
    weight_entry.pack(pady=5, padx=20, fill='x')
    
    tk.Button(frame, text="Save Activity", command=lambda: saveActivity(master, activity_entry, duration_entry, intensity_entry, weight_entry), font=("Helvetica", 12)).pack(pady=20)
    tk.Button(frame, text="Back", command=lambda: switch_frame(master, main_menu), font=("Helvetica", 10)).pack()
    
    return frame


def track_nutrition_page(master):
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
    
    tk.Button(button_frame, text="Save Nutrition Log", command=lambda: saveNutrition(master, calories_entry, protein_entry, carbs_entry, fats_entry), font=("Helvetica", 12)).pack(side="left", padx=10)
    tk.Button(button_frame, text="Back", command=lambda: switch_frame(master, main_menu), font=("Helvetica", 12)).pack(side="right", padx=10)
    
    return frame

def progress_page(master):
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
    
    
    weights = [row for row in read_csv(ACTIVITIES_FILE) if row['username'] == user and 'weight' in row]
    if len(weights) != 0:
        current_weight = float(weights[-1]['weight'])
        if len(weights) > 1:
            weight_change = abs(current_weight - float(weights[0]['weight']))
        else:
            weight_change = 0
    else:
        current_weight = 'N/A'
        weight_change = 'N/A'
    recommendations_text = "Here are some recommendations based on your progress:\n"
    if goals:
        goal = goals[0]
        goal_text = f"Target Weight: {goal.get('target_weight', 'N/A')} kg\nWeekly Workouts: {goal.get('workout_frequency', 'N/A')}"
        if goal.get('target_weight') == current_weight:
            recommendations_text += "You have reached your target weight! Keep up the good work!\n"
        if goal.get('workout_frequency') == total_workouts:
            recommendations_text += "You are meeting your workout frequency goal! Keep it up!\n"
        if total_workouts < int(goal.get('workout_frequency', 0)):
            recommendations_text += f"You have {int(goal.get('workout_frequency', 0)) - total_workouts} workouts left to meet your weekly goal. Keep pushing!\n"
        if total_workouts > int(goal.get('workout_frequency', 0)):
            recommendations_text += f"You have exceeded your goal by {int(goal.get('workout_frequency', 0)) - total_workouts} workouts. Great job!\n"
        if current_weight > float(goal.get('target_weight', 0)):
            recommendations_text += f"You are {current_weight - float(goal.get('target_weight', 0))}kgs away from your goal. You can do this!\n"

    progress_report = (f"Progress Report for: {user}\n"
                       f"----------------------------------\n"
                       f"Total Workouts Logged: {total_workouts}\n"
                       f"Total Duration: {total_duration:.2f} minutes\n"
                       f"Estimated Calories Burned: {total_calories_burned:.2f}\n"
                       f"Estimated Steps: {int(estimated_steps)}\n"
                       f"Current Weight: {current_weight} kg\n"
                       f"Weight Change: {weight_change} kg\n\n"
                       f"--- Your Goals ---\n{goal_text}\n\n"
                       f"--- Recomendations ---\n{recommendations_text}\n")
                        
    

    progress_text.config(state=tk.NORMAL)
    progress_text.delete('1.0', tk.END)
    progress_text.insert(tk.END, progress_report)
    progress_text.config(state=tk.DISABLED)

    tk.Button(frame, text="Back to Menu", command=lambda: switch_frame(master, main_menu), font=("Helvetica", 12)).pack(pady=10)
    
    return frame


def set_goal_page(master):
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

    tk.Button(frame, text="Save Goals", command=lambda: saveGoal(master, weight_entry, frequency_entry), font=("Helvetica", 12)).pack(pady=20)
    tk.Button(frame, text="Back", command=lambda: switch_frame(master, main_menu), font=("Helvetica", 10)).pack()
    
    return frame




def main():
    root = tk.Tk()

    root.title("Fitness Tracker")
    root.geometry("400x550")
    root.eval('tk::PlaceWindow . center')

    setupFiles()

    switch_frame(root, login_register_page)

    root.mainloop()


if __name__ == "__main__":
    main()
