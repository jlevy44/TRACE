import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import subprocess
import os
import platform
import time

def detect_os():
    # Detect the operating system
    return platform.system()

def generate_folders():
    global project_dir
    # Open a dialog to select the project directory
    project_dir = filedialog.askdirectory()
    if project_dir:
        # Create folders within the selected directory
        os.makedirs(os.path.join(project_dir, 'workdir'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'workdir/data'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'upload_dir'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'tmpdir'), exist_ok=True)
        messagebox.showinfo("Success", "Folders created successfully!")

def set_port():
    global port
    # Prompt the user to input a port number
    port = simpledialog.askinteger("Input", "Enter port number:", minvalue=1024, maxvalue=65535)
    if port:
        messagebox.showinfo("Success", f"Port set to {port}")

def run_application():
    global port, project_dir, docker_image_path
    if port is None:
        messagebox.showerror("Error", "Please set the port first!")
        return
    if project_dir is None:
        messagebox.showerror("Error", "Please select the project directory first!")
        return

    command = ""
    if detect_os() == "Windows":
        # Command for Windows to open PowerShell, change directory, and run Docker
        command = (
            f"powershell -Command \"cd '{project_dir}'; "
            f"docker run -d -h localhost -p {port}:{port} "
            f"-v {project_dir}/workdir:/workdir "
            f"-v {project_dir}/upload_dir:/upload_dir "
            f"-v {project_dir}/tmpdir:/tmpdir "
            f"-v {project_dir}:/pwd -w /workdir --rm trace_update:latest trace {port}\""
        )
    elif detect_os() == "Darwin":  # macOS
        # Command for macOS to open a terminal, change directory, and run Docker
        command = (
            f"cd {project_dir} && "
            f"docker run -d -h localhost -p {port}:{port} "
            f"-v {project_dir}/workdir:/workdir "
            f"-v {project_dir}/upload_dir:/upload_dir "
            f"-v {project_dir}/tmpdir:/tmpdir "
            f"-v {project_dir}:/pwd -w /workdir --rm trace_update:latest trace {port}"
        )

    try:
        # Execute the command in a subprocess
        subprocess.run(command, shell=True)
        time.sleep(5)
        url = f"http://127.0.0.1:{port}/"
        root.clipboard_clear()
        root.clipboard_append(url)
        root.update()  # now it stays on the clipboard after the window is closed
        messagebox.showinfo("Success", f"TRACE running on {url} (copied to clipboard)")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run application: {e}")

def quit_application():
    global port
    if port:
        try:
            # Find the container ID using the port
            command = (
                "docker ps --filter "
                f"publish={port} -q"
            )
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            container_id = result.stdout.strip().decode('utf-8')
            if container_id:
                subprocess.run(f"docker stop {container_id}", shell=True)
                messagebox.showinfo("Success", "TRACE has been terminated.")
            else:
                messagebox.showinfo("Error", "No TRACE container found running on the specified port.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to terminate TRACE: {e}")
    else:
        messagebox.showinfo("Error", "No TRACE process is running.")

def share_docker_image():
    global docker_image_path
    # Open a dialog to select the Docker image file
    docker_image_path = filedialog.askopenfilename(filetypes=[("Docker Tar Image File", "*.tar")])
    if docker_image_path:
        messagebox.showinfo("Selected File", f"Docker Tar Image File: {docker_image_path}")
        try:
            # Execute the command in a subprocess
            subprocess.run(f"docker load -i {docker_image_path}", shell=True)
            messagebox.showinfo("Success", f"TRACE docker image has been loaded.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load docker image: {e}")


# Initialize global variables
port = None
project_dir = None
docker_image_path = None

# Create the main window
root = tk.Tk()
root.title("TRACE Application")

# Configure the grid to ensure the buttons are the same size
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
# root.rowconfigure(2, weight=1)  # Add another row for the quit button


# Create and place the buttons in a 2x2 grid with numbers and uniform size
share_image_button = tk.Button(root, text="Upload Docker Image (only once)", command=share_docker_image)
share_image_button.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

generate_button = tk.Button(root, text="1. Set Project Folder", command=generate_folders)
generate_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

set_port_button = tk.Button(root, text="2. Set Port", command=set_port)
set_port_button.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

run_button = tk.Button(root, text="3. Run TRACE", command=run_application)
run_button.grid(row=2, column=0, columnspan=1, padx=10, pady=10, sticky="nsew")

# Add the quit button to terminate the subprocess
quit_button = tk.Button(root, text="4. Quit TRACE", command=quit_application)
quit_button.grid(row=2, column=1, columnspan=1, padx=10, pady=10, sticky="nsew")

# Start the Tkinter event loop
root.mainloop()
