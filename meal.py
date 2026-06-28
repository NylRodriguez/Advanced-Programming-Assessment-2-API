import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO

class MealDataSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Meal Data Interface")
        self.root.geometry("1100x850")
        self.root.configure(bg="#1e1e1e")
        
        self.search_url = "https://www.themealdb.com/api/json/v1/1/search.php?s="
        self.random_url = "https://www.themealdb.com/api/json/v1/1/random.php"
        
        self.favorites_list = []
        self.setup_ui()

    def setup_ui(self):
        self.colors = {
            "bg": "#1e1e1e",
            "sidebar": "#252526",
            "accent": "#007acc",
            "hover": "#1e90ff",
            "text": "#cccccc",
            "terminal": "#1a1a1a"
        }

        self.left_panel = tk.Frame(self.root, bg=self.colors["bg"])
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=30, pady=20)

        self.right_sidebar = tk.Frame(self.root, bg=self.colors["sidebar"], width=280)
        self.right_sidebar.pack(side=tk.RIGHT, fill=tk.Y)

        self.img_container = tk.Label(
            self.left_panel, 
            text="SELECT A MEAL TO BEGIN", 
            bg=self.colors["sidebar"], 
            fg=self.colors["text"], 
            font=("Segoe UI", 12),
            width=80, height=25,
            relief="flat"   
        )
        self.img_container.pack(pady=(0, 20), fill=tk.BOTH, expand=True)

        self.console_output = tk.Text(
            self.left_panel, 
            height=12, 
            bg=self.colors["terminal"], 
            fg=self.colors["text"], 
            font=("Consolas", 11), 
            state='disabled', 
            wrap=tk.WORD, 
            padx=15, pady=15,
            borderwidth=0
        )
        self.console_output.pack(fill=tk.X)

        tk.Label(
            self.right_sidebar, 
            text="COMMAND CENTER", 
            font=("Segoe UI", 11, "bold"), 
            bg=self.colors["sidebar"], 
            fg="#ffffff"
        ).pack(pady=(40, 20))

        self.query_entry = tk.Entry(
            self.right_sidebar, 
            width=22, 
            font=("Segoe UI", 11), 
            bg="#3c3c3c", 
            fg="white", 
            insertbackground="white",
            borderwidth=0
        )
        self.query_entry.pack(pady=10, padx=20)
        self.query_entry.bind("<Return>", lambda e: self.request_data("search"))

        self.create_sidebar_button("Search", lambda: self.request_data("search"))
        self.create_sidebar_button("Random", lambda: self.request_data("random"))
        
        tk.Frame(self.right_sidebar, height=1, bg="#444444").pack(fill=tk.X, pady=30, padx=20)

        self.create_sidebar_button("Save", self.save_record)
        self.create_sidebar_button("Remove", self.delete_record)

        tk.Label(
            self.right_sidebar, 
            text="SAVED RECORDS", 
            font=("Segoe UI", 8, "bold"), 
            bg=self.colors["sidebar"], 
            fg="#888888"
        ).pack(pady=(30, 5))

        self.db_listbox = tk.Listbox(
            self.right_sidebar, 
            height=12, 
            width=28, 
            bg=self.colors["terminal"], 
            fg=self.colors["text"], 
            font=("Segoe UI", 10),
            borderwidth=0,
            highlightthickness=0,
            selectbackground=self.colors["accent"]
        )
        self.db_listbox.pack(pady=5, padx=20)

    def create_sidebar_button(self, text, command):
        btn = tk.Button(
            self.right_sidebar, 
            text=text, 
            command=command,
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["accent"], 
            fg="white",
            activebackground=self.colors["hover"],
            activeforeground="white",
            relief="flat",
            width=18,
            pady=10,
            cursor="hand2"
        )
        btn.pack(pady=8)
        
        btn.bind("<Enter>", lambda e: btn.config(bg=self.colors["hover"]))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.colors["accent"]))

    def request_data(self, mode):
        query = self.query_entry.get()
        target_url = self.random_url if mode == "random" else f"{self.search_url}{query}"
        
        try:
            response = requests.get(target_url)
            payload = response.json()
            if payload['meals']:
                self.process_display(payload['meals'][0])
            else:
                messagebox.showwarning("System", "No results found.")
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {str(e)}")

    def process_display(self, meal_data):
        self.active_record = meal_data['strMeal']
        
        self.console_output.config(state='normal')
        self.console_output.delete(1.0, tk.END)
        header = f"MEAL: {meal_data['strMeal'].upper()}\n"
        header += f"CATEGORY: {meal_data['strCategory']} | ORIGIN: {meal_data['strArea']}\n"
        header += "-"*60 + "\n"
        self.console_output.insert(tk.END, header)
        self.console_output.insert(tk.END, f"INSTRUCTIONS:\n{meal_data['strInstructions']}")
        self.console_output.config(state='disabled')

        try:
            img_res = requests.get(meal_data['strMealThumb'])
            raw_img = Image.open(BytesIO(img_res.content))
            refined_img = raw_img.resize((750, 480), Image.Resampling.LANCZOS)
            photo_data = ImageTk.PhotoImage(refined_img)
            self.img_container.config(image=photo_data, text="")
            self.img_container.image = photo_data 
        except:
            self.img_container.config(image='', text="FAILED TO LOAD IMAGE")

    def save_record(self):
        if hasattr(self, 'active_record') and self.active_record not in self.favorites_list:
            self.favorites_list.append(self.active_record)
            self.db_listbox.insert(tk.END, f"  {self.active_record}")

    def delete_record(self):
        selection = self.db_listbox.curselection()
        if selection:
            entry_text = self.db_listbox.get(selection).strip()
            self.favorites_list.remove(entry_text)
            self.db_listbox.delete(selection)

if __name__ == "__main__":
    app_root = tk.Tk()
    MealDataSystem(app_root)
    app_root.mainloop()