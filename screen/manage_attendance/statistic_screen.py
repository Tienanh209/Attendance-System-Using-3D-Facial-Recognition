# import tkinter as tk
# from tkinter import ttk, filedialog
# import pandas as pd
#
# class StudentStatisticApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Student Attendance Statistics")
#         self.root.geometry("800x600")
#         self.root.configure(bg="#E3F2FD")
#
#         # Title Label
#         self.title_label = tk.Label(self.root, text="Student Attendance Statistics", font=("Arial", 18, "bold"), bg="#E3F2FD")
#         self.title_label.pack(pady=10)
#
#         # Load File Button
#         self.load_button = tk.Button(self.root, text="Load Excel File", font=("Arial", 12, "bold"), bg="#64B5F6", fg="white",
#                                      command=self.load_excel_file)
#         self.load_button.pack(pady=10)
#
#         # Treeview for displaying data
#         self.tree_frame = tk.Frame(self.root)
#         self.tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)
#
#         self.tree_scroll = ttk.Scrollbar(self.tree_frame)
#         self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
#
#         self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll.set)
#         self.tree.pack(fill=tk.BOTH, expand=True)
#
#         self.tree_scroll.config(command=self.tree.yview)
#
#     def load_excel_file(self):
#         file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
#         if not file_path:
#             return
#
#         try:
#             df = pd.read_excel(file_path)
#             self.display_data(df)
#         except Exception as e:
#             tk.messagebox.showerror("Error", f"Failed to load file: {e}")
#
#     def display_data(self, df):
#         # Clear old data
#         self.tree.delete(*self.tree.get_children())
#         self.tree['columns'] = list(df.columns)
#         self.tree['show'] = 'headings'
#
#         for col in df.columns:
#             self.tree.heading(col, text=col)
#             self.tree.column(col, width=100, anchor=tk.CENTER)
#
#         for row in df.itertuples(index=False):
#             self.tree.insert('', tk.END, values=row)
#
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = StudentStatisticApp(root)
#     root.mainloop()
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from pandastable import Table

os.chdir(os.path.dirname(__file__))




class statisticExcel:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Attendance Statistics")
        self.root.geometry("900x600")
        self.root.configure(bg="#E3F2FD")

        # Lớp học
        self.class_folders = self.get_class_folders()
        print("Current Working Directory:", os.getcwd())

        # Tạo Combobox để chọn lớp
        tk.Label(self.root, text="Select Class:", font=("Arial", 14, "bold"), bg="#E3F2FD").pack(pady=10)

        self.class_var = tk.StringVar()
        self.class_combobox = ttk.Combobox(self.root, textvariable=self.class_var, font=("Arial", 12))
        self.class_combobox["values"] = self.class_folders
        self.class_combobox.pack(pady=5)
        self.class_combobox.bind("<<ComboboxSelected>>", self.load_excel_file)

        # Frame hiển thị bảng dữ liệu
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.table = None

    def get_class_folders(self):
        """Lấy danh sách các thư mục lớp học từ thư mục hiện tại."""
        base_path = os.getcwd()  # Thư mục làm việc hiện tại
        class_folders = [f for f in os.listdir(base_path) if os.path.isdir(f) and f.startswith("DI")]
        return class_folders

    def find_excel_file(self, folder):
        """Tìm file Excel đầu tiên trong thư mục lớp học."""
        folder_path = os.path.join(os.getcwd(), folder)
        for file in os.listdir(folder_path):
            if file.endswith(".xlsx") and not file.startswith("~$"):
                return os.path.join(folder_path, file)
        return None

    def load_excel_file(self, event=None):
        """Tải dữ liệu từ file Excel khi chọn lớp học."""
        selected_class = self.class_var.get()
        excel_file = self.find_excel_file(selected_class)

        if not excel_file:
            messagebox.showerror("Error", f"No Excel file found in {selected_class}")
            return

        try:
            df = pd.read_excel(excel_file)
            df['STT'] = df['STT'].fillna(0).astype(int)

            self.display_table(df)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Excel file: {e}")

    def display_table(self, df):
        """Hiển thị dữ liệu lên giao diện Tkinter bằng pandastable."""
        if self.table:
            self.table.destroy()

        self.table = Table(self.frame, dataframe=df, showtoolbar=True, showstatusbar=True)
        self.table.show()
        self.table.redraw()


if __name__ == "__main__":
    root = tk.Tk()
    app = statisticExcel(root)
    root.mainloop()



