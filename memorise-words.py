import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")

class ScrollableFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        appearance = ctk.get_appearance_mode()
        if appearance == "Dark":
            bg_color = "gray17"
        else:
            bg_color = "gray86"

        self.canvas = tk.Canvas(self, borderwidth=0, background=bg_color)
        self.scrollbar = ctk.CTkScrollbar(self, orientation='vertical', command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.scrollable_frame.bind("<Enter>", self._bind_to_mousewheel)
        self.scrollable_frame.bind("<Leave>", self._unbind_from_mousewheel)

    def _on_mousewheel(self, event):
        # Windows and MacOS have different mouse wheel delta values
        if os.name == 'nt':  # For Windows
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else: # linux suppotr
            self.canvas.yview_scroll(int(-1 * (event.delta)), "units")

    def _bind_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  

    def _unbind_from_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")


class GreekLearningApp(ctk.CTk):
    def __init__(self, rows=50):  
        super().__init__()

        self.title("Greek Learning App")
        self.geometry("900x700")  
        self.minsize(800, 600)    
        self.resizable(True, True)  
        self.data_file = "words.json"

        header_frame = ctk.CTkFrame(self)
        header_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(header_frame, text="English", width=400, anchor="center", font=("Arial", 16)).grid(row=0, column=0, padx=10, sticky="ew")
        ctk.CTkLabel(header_frame, text="Greek", width=400, anchor="center", font=("Arial", 16)).grid(row=0, column=1, padx=10, sticky="ew")

        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)

      
        self.entries_frame_container = ScrollableFrame(self)
        self.entries_frame_container.pack(pady=10, padx=10, fill="both", expand=True)

        self.entries = [] 

        for i in range(rows):
            self.add_entry_row(i)

        self.entries_frame_container.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.entries_frame_container.scrollable_frame.grid_columnconfigure(1, weight=1)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)

        save_button = ctk.CTkButton(button_frame, text="Save Progress", command=self.save_progress)
        save_button.grid(row=0, column=0, padx=10)

        load_button = ctk.CTkButton(button_frame, text="Load Progress", command=self.load_progress)
        load_button.grid(row=0, column=1, padx=10)

        add_more_button = ctk.CTkButton(button_frame, text="Add More", command=self.add_more_entries)
        add_more_button.grid(row=0, column=2, padx=10)

        self.load_progress_initial()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def add_entry_row(self, row):
        english_entry = ctk.CTkEntry(
            self.entries_frame_container.scrollable_frame,
            width=400,
            placeholder_text="Enter English word"
        )
        greek_entry = ctk.CTkEntry(
            self.entries_frame_container.scrollable_frame,
            width=400,
            placeholder_text="Enter Greek translation"
        )

        english_entry.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        greek_entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")

        self.entries.append((english_entry, greek_entry))

        english_entry.bind("<Return>", lambda event, row=row: self.focus_greek(row))
        greek_entry.bind("<Return>", lambda event, row=row: self.focus_next_english(row))

    def add_more_entries(self):
        current_rows = len(self.entries)
        additional_rows = 20 
        for i in range(current_rows, current_rows + additional_rows):
            self.add_entry_row(i)
        messagebox.showinfo("Info", f"Added {additional_rows} more entries.")

    def focus_greek(self, row):
        if 0 <= row < len(self.entries):
            greek_entry = self.entries[row][1]
            greek_entry.focus()

    def focus_next_english(self, row):
        next_row = row + 1
        if next_row >= len(self.entries):
            next_row = 0 
        english_entry = self.entries[next_row][0]
        english_entry.focus()

    def save_progress(self):
        data = []
        for english_entry, greek_entry in self.entries:
            english_text = english_entry.get().strip()
            greek_text = greek_entry.get().strip()
            if english_text or greek_text:  
                data.append({"english": english_text, "greek": greek_text})

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=self.data_file,
            title="Save Progress As"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Success", f"Progress saved to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save progress.\n{e}")

    def load_progress_initial(self):
        """
        Load progress from the default data file if it exists.
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.populate_entries(data)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load existing progress.\n{e}")

    def load_progress(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Open Progress File"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.populate_entries(data)
                messagebox.showinfo("Success", f"Progress loaded from {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load progress.\n{e}")

    def populate_entries(self, data):
        for english_entry, greek_entry in self.entries:
            english_entry.delete(0, tk.END)
            greek_entry.delete(0, tk.END)

        # Populate entries with loaded data
        for i, word_pair in enumerate(data):
            # Add more rows if necessary
            if i >= len(self.entries):
                self.add_entry_row(i)
            english_entry, greek_entry = self.entries[i]
            english_entry.insert(0, word_pair.get("english", ""))
            greek_entry.insert(0, word_pair.get("greek", ""))

    def on_closing(self):
        if messagebox.askokcancel("Quit", "do you want to save your progress befo exiting?"):
            self.save_progress()
        self.destroy()


if __name__ == "__main__":
    app = GreekLearningApp(rows=50) 
    app.mainloop()
