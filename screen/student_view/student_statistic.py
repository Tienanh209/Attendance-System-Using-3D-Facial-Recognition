import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd

class StudentStatisticApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Attendance Statistics")
        self.root.geometry("800x600")
        self.root.configure(bg="#E3F2FD")

        # Title Label
        self.title_label = tk.Label(self.root, text="Student Attendance Statistics", font=("Arial", 18, "bold"), bg="#E3F2FD")
        self.title_label.pack(pady=10)

        # Load File Button
        self.load_button = tk.Button(self.root, text="Load Excel File", font=("Arial", 12, "bold"), bg="#64B5F6", fg="white",
                                     command=self.load_excel_file)
        self.load_button.pack(pady=10)

        # Treeview for displaying data
        self.tree_frame = tk.Frame(self.root)
        self.tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll.set)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree_scroll.config(command=self.tree.yview)

    def load_excel_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)
            self.display_data(df)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to load file: {e}")

    def display_data(self, df):
        # Clear old data
        self.tree.delete(*self.tree.get_children())
        self.tree['columns'] = list(df.columns)
        self.tree['show'] = 'headings'

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)

        for row in df.itertuples(index=False):
            self.tree.insert('', tk.END, values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentStatisticApp(root)
    root.mainloop()