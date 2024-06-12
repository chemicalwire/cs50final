import tkinter as tk
from tkinter import messagebox

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("400x300")  # Set the window size to 400x300 pixels
        self.create_widgets()

    def create_widgets(self):
        ok_button = tk.Button(self.root, text="OK", command=self.on_ok_click)
        ok_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def on_ok_click(self):
        messagebox.showinfo("Message", "OK button clicked!")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()