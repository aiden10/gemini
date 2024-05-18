import tkinter as tk
from tkinter import ttk

class Overlay:
    def __init__(self, text):
        self.root = tk.Tk()
        self.create_overlay(text)

    def create_overlay(self, text):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 300
        window_height = 50
        x_position = 0
        y_position = screen_height - window_height
        
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        
        frame = ttk.Frame(self.root, padding="3 3 12 12", relief="solid", borderwidth=2, style="Overlay.TFrame")
        frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.label = ttk.Label(frame, text=text, style="Overlay.TLabel")
        self.label.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        for child in frame.winfo_children():
            child.grid_configure(padx=5, pady=5)
        
        style = ttk.Style()
        style.configure("Overlay.TFrame", background="black")
        style.configure("Overlay.TLabel", background="black", foreground="white", font=("Helvetica", 16))
    
    def show(self):
        self.root.deiconify()
    
    def hide(self):
        self.root.withdraw()
    
    def destroy(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()

    def update_text(self, new_text):
        self.label.config(text=new_text)
    
    def start(self):
        self.root.after(0, self.run)
        self.root.mainloop()

