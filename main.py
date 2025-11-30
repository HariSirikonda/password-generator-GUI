import tkinter
from tkinter import *
from tkinter import ttk
from random import randint
from tkinter import messagebox
import datetime
import re
import sqlite3

# Connect to SQLite Database
conn = sqlite3.connect('passwords.db')
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        char_length INTEGER,
        password TEXT,
        strength TEXT,
        date TEXT
    )
''')
conn.commit()

today = datetime.date.today()
formatted_date = today.strftime('%d/%m/%Y')

# Password strength checker
def check_password_strength(password):
    length_regex = re.compile(r'.{8,}')
    uppercase_regex = re.compile(r'[A-Z]')
    lowercase_regex = re.compile(r'[a-z]')
    digit_regex = re.compile(r'\d')
    symbol_regex = re.compile(r'[!@#$%^&*()_+=\[{\]}\|\\:;\"\'<,>\.?/`~]')
    strength_score = 0
    if length_regex.search(password):
        strength_score += 1
    if uppercase_regex.search(password):
        strength_score += 1
    if lowercase_regex.search(password):
        strength_score += 1
    if digit_regex.search(password):
        strength_score += 1
    if symbol_regex.search(password):
        strength_score += 1
    return strength_score

# Generate password
def generate_password():
    number = EntryBox_2.get()
    if number.isdigit():
        result_entry.delete(0, END)
        password_length = int(EntryBox_2.get())
        Generated_password = ''
        for x in range(password_length):
            Generated_password += chr(randint(33, 126))
        result_entry.insert(0, Generated_password)

        # Check the strength of the password
        strength_score = check_password_strength(Generated_password)
        if strength_score <= 2:
            strength_label.config(text="Weak", fg="red")
        elif strength_score <= 4:
            strength_label.config(text="Moderate", fg="orange")
        else:
            strength_label.config(text="Strong", fg="green")
    else:
        messagebox.showwarning("PASSWORD GENERATOR", "Please enter a valid number!")

# Copy to clipboard
def clipper():
    app.clipboard_clear()
    app.clipboard_append(result_entry.get())
    save_info.delete(0, END)
    save_info.insert(0, "Copied To Clipboard..!")

# Save password to database
def save_password():
    name = EntryBox_1.get()
    char_length = EntryBox_2.get()
    password = result_entry.get()
    strength = strength_label.cget("text")
    current_date = formatted_date  # Today's date

    if name and char_length.isdigit() and password:
        cursor.execute('''
            INSERT INTO passwords (name, char_length, password, strength, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, int(char_length), password, strength, current_date))
        conn.commit()

        save_info.delete(0, END)
        save_info.insert(0, "Password Saved to Database!")
    else:
        save_info.delete(0, END)
        save_info.insert(0, "Invalid input, try again.")

def searchPassword():
    Button_1.config(state='disabled')
    DeleteButton.config(state="normal")
    Button_3.config(text="Re Save Password")
    passwordName = EntryBox_1.get()
    cursor.execute('SELECT * FROM passwords WHERE name = ?', (passwordName,))
    result = cursor.fetchone()
    if result is None:
        Button_1.config(state='disabled')
        Button_2.config(state='disabled')
        Button_3.config(state='disabled')
        result_entry.delete(0, END)
        result_entry.insert(0, "Not Found !")
    else:
        searchedPassword = result[3]
        searchedLength = result[2]
        strength_score = check_password_strength(searchedPassword)
        if strength_score <= 2:
            strength_label.config(text="Weak", fg="red")
        elif strength_score <= 4:
            strength_label.config(text="Moderate", fg="orange")
        else:
            strength_label.config(text="Strong", fg="green")
        result_entry.delete(0, END)
        EntryBox_2.delete(0, END)
        EntryBox_2.insert(0, searchedLength)
        result_entry.insert(0, searchedPassword)

def Reset():
    EntryBox_1.delete(0, END)
    EntryBox_2.delete(0, END)
    result_entry.delete(0, END)
    Button_1.config(state="normal")
    Button_2.config(state="normal")
    Button_3.config(state="normal", text="Save Passoword")

def updatePassword():
    passwordname = EntryBox_1.get()
    newPassword = result_entry.get()

    cursor.execute("SELECT * FROM passwords WHERE name = ?", (passwordname,))
    result = cursor.fetchone()

    if result:
        cursor.execute("UPDATE passwords SET char_length = ?, password = ?, strength = ?, date = ? WHERE name = ?",
                       (len(newPassword), newPassword, check_password_strength(newPassword), formatted_date, passwordname))
        conn.commit()
    save_info.delete(0, END)
    save_info.insert(0, "Password Updated :)")
    Reset()

def delete_password():
    PasswordName = EntryBox_1.get()
    cursor.execute("DELETE FROM passwords WHERE name = ?", (PasswordName,))
    conn.commit()

    if cursor.rowcount > 0:
        save_info.delete(0, END)
        save_info.insert(0, "Password Delete..!")
    else:
        save_info.delete(0, END)
        save_info.insert(0, "Problem Deleting..!")
    Reset()
# Handle closing event
def on_closing():
    conn.close()
    app.destroy()

app = tkinter.Tk()
app.title("PASSWORD GENERATOR")
app.geometry("600x400")
app.protocol("WM_DELETE_WINDOW", on_closing)

LabelFrame = ttk.LabelFrame(app, text="Name the Password : ")
LabelFrame.pack(pady=10)

EntryBox_1 = tkinter.Entry(LabelFrame, font=("Helvetica", 18))
EntryBox_1.grid(row=0, column=0, pady=10, padx=10)

SearchButton = tkinter.Button(LabelFrame, text="Search", font=("Helvetica", 10), command=searchPassword)
SearchButton.grid(row=0, column=1, pady=10, padx=10)

LabelFrame = ttk.LabelFrame(app, text="How many characters do you want : ")
LabelFrame.pack(pady=10)

EntryBox_2 = tkinter.Entry(LabelFrame, font=("Helvetica", 18))
EntryBox_2.grid(row=0, column=0, pady=10, padx=10)

ResetButton = tkinter.Button(LabelFrame, text="Reset", font=("Helvetica", 10), command=Reset)
ResetButton.grid(row=0, column=1, pady=10, padx=10)

result_frame = ttk.LabelFrame(app, text="The Password :")
result_frame.pack(pady=10, padx=10)

result_entry = tkinter.Entry(result_frame, font=("Helvetica", 18), bd=0, bg="systembuttonface")
result_entry.grid(row=0, column=0, padx=10, pady=10)

strength_label = tkinter.Label(result_frame, text="Strength")
strength_label.grid(row=0, column=1, padx=10, pady=10)

updateButton = tkinter.Button(result_frame, text="Update", font=("Helvetica", 10), command=updatePassword)
updateButton.grid(row=0, column=2, padx=10, pady=10)

DeleteButton = tkinter.Button(result_frame, text="Delete", font=("Helvetica", 10), command=delete_password, state="disabled")
DeleteButton.grid(row=0, column=3, padx=10, pady=10)

Buttonframe = ttk.LabelFrame(app, text="Functions")
Buttonframe.pack(pady=10)

Button_1 = tkinter.Button(Buttonframe, text="Generate password", font=("Helvetica", 8), bg="white", fg="black", command=generate_password)
Button_1.grid(row=0, column=0, padx=10, pady=10)

Button_3 = tkinter.Button(Buttonframe, text="Regenerate", font=("Helvetica", 8), bg="white", fg="black", command=generate_password)
Button_3.grid(row=0, column=1, padx=10, pady=10)

Button_2 = tkinter.Button(Buttonframe, text="Copy To Clipboard", font=("Helvetica", 8), bg="white", fg="black", command=clipper)
Button_2.grid(row=0, column=2, padx=10, pady=10)

Button_3 = tkinter.Button(Buttonframe, text="Save Password", font=("Helvetica", 8), bg="white", fg="black", command=save_password)
Button_3.grid(row=0, column=3, padx=10, pady=10)

save_info = tkinter.Entry(app, font=("Helvetica", 18), bg="systembuttonface", bd=0)
save_info.pack(pady=5)

app.mainloop()