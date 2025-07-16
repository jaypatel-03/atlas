import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess

def run_long_process(command, on_done):
    """Run a long process in a separate thread and call on_done when finished."""
    def task():
        subprocess.run(command, shell=True)  # Blocking call
        on_done()  # callback in main thread
    threading.Thread(target=task, daemon=True).start()

def show_progress_popup(root, command):
    popup = tk.Toplevel(root)
    popup.title("Processing...")
    popup.geometry("300x100")
    popup.transient(root)
    popup.grab_set()

    label = tk.Label(popup, text="Please wait...")
    label.pack(pady=10)

    progress = ttk.Progressbar(popup, mode="indeterminate")
    progress.pack(expand=True, fill="x", padx=20, pady=10)
    progress.start(10)  # speed of animation

    def on_done():
        # This runs in the main thread after process finishes
        progress.stop()
        popup.destroy()
        messagebox.showinfo("Done", "Process finished!")

    run_long_process(command, on_done)

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x200")

    btn = tk.Button(root, text="Run Long Task", 
                    command=lambda: show_progress_popup(root, "sleep 5"))
    btn.pack(pady=50)

    root.mainloop()
