import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os 

#set a global standard for the display
app_font= ("Arial",14)
title_font = ("Arial", 18, "bold")
bg_color = "#f0f0f0"
sidebar_color = "#548b54"

#dictionary to hold patient tasks
patient_tasks = {}

#where the task data will be saved 
DATA_FILE = "patients.json"
COMPLETED_FILE="Completed_tasks.json"

#side bar for navigation
def add_sidebar(window, go_back=None):
    sidebar=tk.Frame(window, bg=sidebar_color, width=120)
    sidebar.pack(side="left", fill="y")
    
    tk.Button(
        sidebar,
        text="Home",
        font=app_font,
        bg="gray",
        fg="white",
        command=lambda: go_home(window)
    ).pack(padx=10, pady=10, fill="x")
    
    if go_back:
        tk.Button(
        sidebar,
        text="Go Back",
        font= app_font,
        bg= "gray",
        fg="white",
        command= lambda: go_back(window)).pack(padx=10, pady=10, fill="x")
        
    tk.Button(
        sidebar, 
        text="Exit",
        font=app_font,
        bg="red",
        fg="white",
        command=window.quit        
    ).pack(padx=10, pady=10, fill="x")
   
#clear completed tasks for the selected patient 
def clear_completed_tasks(patient_name):
    if "_completed" in patient_tasks and patient_name in patient_tasks["_completed"]:
        patient_tasks["_completed"][patient_name] = []
        save_tasks_to_file()
        messagebox.showinfo("Completed Tasks Cleared", "All completed tasks have been cleared.")
    else:
        messagebox.showinfo("No Tasks found.", "No completed tasks found to clear.")
        
#load existing tasks
def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,"r") as f:
            return json.load(f)
    return {}

#save all tasks
def save_tasks_to_file():
    with open(DATA_FILE, "w") as f:
        json.dump(patient_tasks, f)

#load the tasks marked complete
def load_completed_tasks():
    if os.path.exists(COMPLETED_FILE):
        with open(COMPLETED_FILE, "r") as f:
            return json.load(f)
    return {}

#save the completed tasks
def save_completed_tasks():
    with open(COMPLETED_FILE, "w") as f:
        json.dump(completed_tasks, f)
        
#load existing tasks when the program starts
patient_tasks = load_tasks()
completed_tasks = load_completed_tasks()  

#convert lists to dicts 
for patient, tasks in list(patient_tasks.items()):
    if isinstance(tasks, list):
        patient_tasks[patient] = {
            "morning":tasks,
            "afternoon": [],
            "evening": []
        }     

#patients button
def handle_patient_button():
    name = simpledialog.askstring("Patient Login", "Enter your name: ")
    if name:
        name = name.strip().lower()
        show_patient_tasks(name)

#caregiver button 
def handle_caregiver_button():
    name = simpledialog.askstring("Caregiver Access", "Enter patient name: ")
    if name:
        name = name.strip().lower()
        caregiver_menu(name)
            
#displays completed tasks for the caregiver to view
def show_completed_tasks(patient_name):
    completed = patient_tasks.get("_completed",{}).get(patient_name,[])
    
    #create window to display completed tasks 
    completed_window = tk.Toplevel()
    completed_window.title(f"Completed Tasks for {patient_name}")
    completed_window.geometry("500x400")
    completed_window.configure(bg="white")
    
    add_sidebar(completed_window, go_back=lambda w: caregiver_menu(patient_name))
    
    tk.Label(
        completed_window,
        text=f"Completed Tasks for {patient_name}",
        font=title_font,
        bg="white"
    ).pack(pady=10)
    
    if completed:        
        for task in completed:
            tk.Label(
                completed_window,
                text= task,
                font=app_font,
                bg="white",
                anchor="w",
                justify="left"
            ).pack(fill="both", padx=20, pady=2)

    else:
        tk.Label(
            completed_window,
            text="No completed tasks yet",
            font=app_font,
            bg="white"
        ).pack(pady=20)

#shows the patient their tasks and allows them to complete them         
def show_patient_tasks(patient_name):
    tasks = patient_tasks.get(patient_name, {"morning":[], "afternoon": [], "evening": []})
    
    #window for the tasks
    task_window = tk.Toplevel()
    task_window.title(f"{patient_name}'s Tasks")
    task_window.geometry("700x500")
    task_window.configure(bg="white")
    
    add_sidebar(task_window)
    
    tk.Label(
        task_window,
        text=f"Tasks for {patient_name}",
        font=title_font,
        bg= "white"
    ).pack(pady=10)
    
    #list to hold checkbox variables
    checkbox_vars = []
    
    #display the tasks in groups based on time of the day
    for time_period in ["morning", "afternoon", "evening"]:
        if tasks.get(time_period):
            tk.Label(
                task_window,
                text=f"{time_period.capitalize()} Tasks",
                font=title_font,
                bg="white"
            ).pack(pady=(10,0))
            
    #display each task with a checkbox
            for task in tasks[time_period]: 
                var = tk.BooleanVar()
                cb = tk.Checkbutton(
                    task_window,
                    text=task,
                    variable=var,
                    font=app_font,
                    bg="white",
                    anchor="w",
                    justify="left"
                )
                cb.pack(fill="both", padx=20, pady=2, anchor="w")
                checkbox_vars.append((var,task))

#function to complete tasks
    def complete_selected_tasks():
        completed = []
        
        for var, task in checkbox_vars:
            if var.get():
                completed.append(task)
                for period in ["morning","afternoon", "evening"]: 
                    if task in patient_tasks[patient_name][period]:
                        patient_tasks[patient_name][period].remove(task)
                        break
        
        if completed:                     
            if "_completed" not in patient_tasks:
                patient_tasks["_completed"] = {}
            if patient_name not in patient_tasks["_completed"]:
                patient_tasks["_completed"][patient_name] = []
            
            patient_tasks["_completed"][patient_name].extend(completed)
            
            #save updates
            save_tasks_to_file()
            
            messagebox.showinfo("Tasks Completed", f"You completed {len(completed)} tasks")
            task_window.destroy()
            show_patient_tasks(patient_name)
        else:
            messagebox.showinfo("Please select a task to complete")
    
    tk.Button(
        task_window,
        text="Complete Selected Tasks",
        command=complete_selected_tasks,
        font=app_font,
    ).pack(pady=10)
                        
#function for caregiver to enter in patient tasks 
def open_task_input_form(patient_name):

    task_window = tk.Toplevel()
    task_window.title(f"Add tasks for {patient_name}")
    task_window.geometry("600x600")
    task_window.configure(bg="white")
    
    add_sidebar(task_window, go_back=lambda w: caregiver_menu(patient_name))
    
    #provide a list of options by default for the caregiver to choose from based on alzheimers.org recommendations 
    categories= {
        "Household chores":["Do a load of Laundry", "Go Grocery Shopping", "Balance the check book", "Do the dishes", "Make the bed", "Sweep and mop", "Set the table", "Put away dishes", "Other"],
        "Meal time":["Make breakfast", "Make lunch", "Make dinner", "Have a snack", "Bake some cookies", "Other"],
        "Personal Care": ["Take a shower", "Take a bath", "Get dressed", "Brush your hair", "Brush your teeth", "Other"],
        "Creative Activities":["Listen to music", "Look at family photos", "Play a card game", "Do a puzzle", "Read a book", "Watch a movie","Other"],
        "Healthcare":["Take medication", "Other"],
        "Physical":["Go for a walk", "Plant flowers", "Water the plants", "Feed the birds", "Go to the park", "Have a picnic", "Sit on the porch with a drink", "Other"],
        "Miscellaneous":["Other"]
        }
    
    #create a drop down for the categories
    selected_category=tk.StringVar()
    selected_category.set(next(iter(categories)))

    time_of_day = tk.StringVar(value="morning")
    tk.Label(task_window,
             text="Select Time of Day:",
             font=app_font,
             bg="white").pack(pady=5)
    tk.OptionMenu(task_window,
                  time_of_day,
                  "morning",
                  "afternoon",
                  "evening").pack()
    
    tk.Label(
        task_window,
        text= "Enter time (e.g. 8:00 AM):",
        font=app_font,
        bg="white").pack(pady=5)
    
    task_time_var= tk.StringVar()
    tk.Entry(task_window, textvariable=task_time_var).pack()

    task_vars = {}
    checkboxes_frame = tk.Frame(task_window)
    checkboxes_frame.pack(pady=10)
    
    custom_task_var = tk.StringVar()
    
    #updates the task checkboxes when a category is selected 
    def update_checkboxes(*args):
        #clear existing checkboxes in the frame
        for widget in checkboxes_frame.winfo_children():
            widget.destroy()
            
        task_vars.clear()
        category = selected_category.get()
        
        
        if category in categories:
            for task in categories[category]:
                var = tk.BooleanVar()
                cb = tk.Checkbutton(checkboxes_frame, text=task, variable=var)
                cb.pack(anchor="w")
                task_vars[task] = var
                
        tk.Label(checkboxes_frame, text="Other:").pack(anchor="w", pady=(10,0))
        tk.Entry(checkboxes_frame, textvariable=custom_task_var).pack(anchor="w")

#save selected tasks for the patients
    def save_selected_tasks():
        if patient_name not in patient_tasks:
            patient_tasks[patient_name] = {"morning": [], "afternoon": [], "evening": []}
            
        new_tasks = []
        
        time_str= task_time_var.get().strip()
        if not time_str:
            messagebox.showerror("Missing Time", "Please enter a time for this task")
            return
        
        for task, var in task_vars.items():
            if var.get():
                new_tasks.append(f"{time_str} - {task}")
                
        if custom_task_var.get().strip():
            new_tasks.append(f"{time_str} - {custom_task_var.get().strip()}")
            
        patient_tasks[patient_name][time_of_day.get()].extend(new_tasks)
        save_tasks_to_file()
        tk.messagebox.showinfo("Tasks saved", f"Added {len(new_tasks)} tasks for {patient_name}")
        
        for var in task_vars.values():
            var.set(False)
        custom_task_var.set("")
        
    tk.Label(task_window, text="Select Category:", font=app_font).pack(pady=5)
    tk.OptionMenu(
        task_window, 
        selected_category,
        *categories.keys(),
        command= update_checkboxes).pack()
        
    checkboxes_frame.pack(pady=10)
    update_checkboxes()
    
    tk.Button(
        task_window,
        text="Save Selected Tasks",
        command=save_selected_tasks
    ).pack(pady=10)

#create the caregivers main menu        
def caregiver_menu(patient_name):
    #create the window 
    menu_window= tk.Toplevel()
    menu_window.title(f"Caregiver Menu for {patient_name}")
    menu_window.geometry("600x500")
    menu_window.configure(bg="white")
    
    add_sidebar(menu_window)
    
    tk.Label(
        menu_window,
        text=f"Caregiver options for {patient_name}",
        font=title_font,
        bg="white"
    ).pack(pady=20)
    
    tk.Button(
        menu_window,
        text="Add new tasks",
        command=lambda: open_task_input_form(patient_name),
        font=app_font,
        width=20
    ).pack(pady=10)
    
    tk.Button(
        menu_window,
        text="View completed tasks",
        command=lambda: show_completed_tasks(patient_name),
        font=app_font,
        width=20
    ).pack(pady=10)
    
    tk.Button(
    menu_window,
    text="Clear Completed Tasks",
    command=lambda: clear_completed_tasks(patient_name),
    font=app_font,
    width=20
    ).pack(pady=10)

#return to the home screen  
def go_home(current_window):
    current_window.destroy()
    create_main_window()

#main gui function 
def create_main_window():
    root = tk.Tk()
    root.title("Caregiver Assistant")
    root.geometry("700x500")
    root.configure(bg=bg_color)
    
    #create side bar navigation
    sidebar=tk.Frame(root, bg=sidebar_color, width=150)
    sidebar.pack(side="left", fill="y")
    
    tk.Button(
        sidebar,
        text="Exit",
        command=root.quit,
        font=app_font,
        bg="#e74c3c",
        fg="white",
        relief="flat"
    ).pack(pady=20, padx=10, fill="x")

    main_frame = tk.Frame(root, bg=bg_color)
    main_frame.pack(side="right", fill="both", expand= True)

#title for the app
    tk.Label(
        main_frame, 
        text="Caregiver Assistant", 
        font=title_font, 
        bg= bg_color,
        fg="#2c3e50"
    ).pack(pady=(40,10))
    
#subtitle for app 
    tk.Label(
        main_frame,
        text="Please select your role:",
        font=app_font,
        bg=bg_color,
        fg="#34496e"
    ).pack(pady=10)
    
    style = {
        "font": ("Arial", 14),
        "bg": "#2980b9",
        "fg": "white",
        "relief" : "flat",
        "width": 20,
        "padx": 10,
        "pady":10
    }

#button for the patient
    tk.Button(
        main_frame,
        text="Patient",
        command=handle_patient_button,
        **style 
        ).pack(pady=10)
    
#button for caregiver
    tk.Button(
        main_frame,
        text="Caregiver",
        command=handle_caregiver_button,
        **style
        ).pack(pady=10)
        
    return root
    
    if __name__ == "__main__":
        create_main_window()

