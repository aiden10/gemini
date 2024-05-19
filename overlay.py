import tkinter as tk
from tkinter import ttk
import queue
import threading

class Overlay:
    def __init__(self, text):
        self.root = tk.Toplevel()
        self.queue = queue.Queue()
        self.create_overlay(text)
        self.start_worker()

    def create_overlay(self, text):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 800
        window_height = 50
        x_position = 0
        y_position = screen_height - window_height

        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        frame = ttk.Frame(self.root, padding="3 3 3 3", relief="solid", borderwidth=2, style="Overlay.TFrame")
        frame.pack(fill=tk.BOTH, expand=True)

        self.label = ttk.Label(frame, text=text, style="Overlay.TLabel")
        self.label.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure("Overlay.TFrame", background="black")
        style.configure("Overlay.TLabel", background="black", foreground="white", font=("Helvetica", 12))

    def update_text(self, new_text):
        self.queue.put(new_text)

    def worker_thread(self):
        while True:
            if not self.queue.empty():
                new_text = self.queue.get()
                self.label.config(text=new_text)
            self.root.update_idletasks()  # Update the GUI

    def start_worker(self):
        thread = threading.Thread(target=self.worker_thread, daemon=True)
        thread.start()

