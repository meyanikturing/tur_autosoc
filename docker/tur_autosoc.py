import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def select_directory():
    directory_path = filedialog.askdirectory()
    if directory_path:
        dir_entry.delete(0, tk.END)
        dir_entry.insert(0, directory_path)

def execute_script():
    script_path = file_entry.get()
    volume_path = dir_entry.get()
    
    if not os.path.isfile(script_path):
        messagebox.showerror("Error", "Please select a valid Python script file.")
        return

    if not os.path.isdir(volume_path):
        messagebox.showerror("Error", "Please select a valid directory path.")
        return
    
    script_name = os.path.basename(script_path)  # Get only the script filename
    try:
        # Run the Docker command with the script in /workspaces
        command = [
            "docker", "run", "--rm",
            "-v", f"{volume_path}:/workspaces",
            "-w", "/workspaces",
            "meyanik/tur_autosoc:0.01",
            "python3", f"./{script_name}"
        ]
        subprocess.run(command, check=True)
        messagebox.showinfo("Success", "Script executed successfully in Docker.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Execution Error", f"Failed to execute script:\n{e}")

# Set up the main window
root = tk.Tk()
root.title("Docker Python Script Executor")

# Create widgets
file_label = tk.Label(root, text="Select Python Script:")
file_label.grid(row=0, column=0, padx=10, pady=10)
file_entry = tk.Entry(root, width=50)
file_entry.grid(row=0, column=1, padx=10, pady=10)
file_button = tk.Button(root, text="Browse", command=select_file)
file_button.grid(row=0, column=2, padx=10, pady=10)

dir_label = tk.Label(root, text="Select Directory Path:")
dir_label.grid(row=1, column=0, padx=10, pady=10)
dir_entry = tk.Entry(root, width=50)
dir_entry.grid(row=1, column=1, padx=10, pady=10)
dir_button = tk.Button(root, text="Browse", command=select_directory)
dir_button.grid(row=1, column=2, padx=10, pady=10)

execute_button = tk.Button(root, text="Execute", command=execute_script)
execute_button.grid(row=2, column=0, columnspan=3, pady=20)

root.mainloop()
