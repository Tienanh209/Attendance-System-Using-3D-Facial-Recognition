import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import pandas as pd

class StatisticMySQL:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Attendance Statistics")
        self.root.geometry("900x600")
        self.root.configure(bg="#E3F2FD")

        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'face_recognition_sys'
        }

        # Back button
        self.btn_back = tk.Button(self.root, text="Quay lại", font=("Arial", 12, "bold"),
                                  bg="#4699A6", fg="white", width=10, height=2, borderwidth=0,
                                  command=self.close_current_window)
        self.btn_back.place(x=30, y=20)

        # Get class subjects
        self.class_subjects = self.get_class_subjects()

        # Create Combobox to select class subject
        tk.Label(self.root, text="Chọn lớp học :", font=("Arial", 14, "bold"), bg="#E3F2FD").pack(pady=10)

        self.class_var = tk.StringVar()
        self.class_combobox = ttk.Combobox(self.root, textvariable=self.class_var, font=("Arial", 12))
        self.class_combobox["values"] = self.class_subjects
        self.class_combobox.pack(pady=5)
        self.class_combobox.bind("<<ComboboxSelected>>", self.load_attendance_data)

        # Frame to display table
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Treeview will be initialized in display_table
        self.tree = None

    def close_current_window(self):
        """Close the current window without exiting the application."""
        self.root.destroy()

    def get_class_subjects(self):
        """Fetch list of class subjects from the database."""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            query = """
                SELECT id_class_subject
                FROM class_subject
                WHERE year = '2023-2024'
                ORDER BY id_class_subject
            """
            cursor.execute(query)
            class_subjects = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return class_subjects
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch class subjects: {e}")
            return []

    def load_attendance_data(self, event=None):
        """Load attendance data from MySQL for the selected class subject."""
        selected_class = self.class_var.get()
        if not selected_class:
            messagebox.showerror("Error", "Please select a class subject")
            return

        try:
            conn = mysql.connector.connect(**self.db_config)
            query = """
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY s.id_student) AS STT,
                    s.id_student AS 'Mã sinh viên',
                    s.name_student AS 'Họ và tên',
                    s.birthday AS 'Ngày sinh',
                    GROUP_CONCAT(
                        CASE 
                            WHEN a.status = 'Present' THEN 'Có mặt'
                            WHEN a.status = 'Absent' THEN 'Vắng'
                            ELSE 'Đang xác thực'
                        END
                        ORDER BY se.date, se.start_time
                        SEPARATOR ', '
                    ) AS 'Trạng thái điểm danh'
                FROM student s
                LEFT JOIN register r ON s.id_student = r.id_student
                LEFT JOIN attendance a ON s.id_student = a.id_student
                LEFT JOIN session se ON a.id_session = se.id_session
                WHERE r.id_class_subject = %s
                GROUP BY s.id_student, s.name_student, s.birthday
                ORDER BY s.id_student
            """
            df = pd.read_sql_query(query, conn, params=(selected_class,))
            conn.close()

            # Format birthday column
            df['Ngày sinh'] = pd.to_datetime(df['Ngày sinh']).dt.strftime('%Y-%m-%d')

            # Replace NaN values
            columns_to_replace = [col for col in df.columns if col != 'STT']
            df[columns_to_replace] = df[columns_to_replace].fillna("Không dữ liệu")

            # Ensure STT is integer
            df['STT'] = df['STT'].astype(int)

            self.display_table(df)
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to load data: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def display_table(self, df):
        """Display data in Tkinter using ttk.Treeview."""
        # Clear old table if exists
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Create Treeview
        self.tree = ttk.Treeview(self.frame)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Define columns
        columns = list(df.columns)
        self.tree["columns"] = columns
        self.tree["show"] = "headings"

        # Customize Treeview appearance
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview.Heading", background="#0288D1", foreground="#FFFFFF", font=("Arial", 10, "bold"))
        style.configure("Treeview", rowheight=25, font=("Arial", 10), foreground="#000000", background="#FFFFFF", fieldbackground="#FFFFFF")
        style.map("Treeview", background=[('!selected', '#FFFFFF'), ('selected', '#D3D3D3')])
        style.configure("Treeview", bordercolor="#B0BEC5", borderwidth=1)

        # Set column headings and alignment
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=150)

        # Insert data into Treeview
        for index, row in df.iterrows():
            self.tree.insert("", tk.END, values=list(row), tags=("row",))

        # Customize row colors
        self.tree.tag_configure("row", background="#FFFFFF", foreground="#000000")
        self.tree.tag_configure("tree", background="#0288D1", foreground="#FFFFFF")
        for i, item in enumerate(self.tree.get_children()):
            self.tree.item(item, tags=("row", "tree"))

if __name__ == "__main__":
    root = tk.Tk()
    app = StatisticMySQL(root)
    root.mainloop()