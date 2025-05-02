import os
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

os.chdir(os.path.dirname(__file__))

class statisticExcel:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Attendance Statistics")
        self.root.geometry("900x600")
        self.root.configure(bg="#E3F2FD")




        self.btn_back = tk.Button(self.root, text="Quay lại", font=("Arial", 12, "bold"),
                                   bg="#4699A6", fg="white", width=10, height=2, borderwidth=0,
                                   command=self.close_current_window)
        self.btn_back.place(x=30, y=20)
        # Lớp học
        self.class_folders = self.get_class_folders()
        print("Current Working Directory:", os.getcwd())

        # Tạo Combobox để chọn lớp
        tk.Label(self.root, text="Chọn lớp học :", font=("Arial", 14, "bold"), bg="#E3F2FD").pack(pady=10)

        self.class_var = tk.StringVar()
        self.class_combobox = ttk.Combobox(self.root, textvariable=self.class_var, font=("Arial", 12))
        self.class_combobox["values"] = self.class_folders
        self.class_combobox.pack(pady=5)
        self.class_combobox.bind("<<ComboboxSelected>>", self.load_excel_file)

        # Frame hiển thị bảng dữ liệu
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Treeview sẽ được khởi tạo trong display_table
        self.tree = None

    def close_current_window(self):
        """Đóng cửa sổ hiện tại mà không thoát toàn bộ ứng dụng"""
        self.root.destroy()  # Đóng cửa sổ hiện tại
    def get_class_folders(self):
        """Lấy danh sách các thư mục lớp học từ thư mục hiện tại."""
        base_path = os.getcwd()
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

            # Đổi tên cột "Birth" thành "Ngày sinh"
            df = df.rename(columns={"Birth": "Ngày sinh"})

            # Thay thế tất cả giá trị "nan" bằng "Không dữ liệu" trong DataFrame (trừ cột STT)
            columns_to_replace = [col for col in df.columns if col != 'STT']
            df[columns_to_replace] = df[columns_to_replace].fillna("Không dữ liệu")

            # Thay thế các giá trị "Pending", "Present", "Not yet"
            df[columns_to_replace] = df[columns_to_replace].replace({
                "Pending": "Đang xác thực",
                "Present": "Có mặt",
                "Not yet": "Vắng"
            })

            self.display_table(df)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Excel file: {e}")

    def display_table(self, df):
        """Hiển thị dữ liệu lên giao diện Tkinter bằng ttk.Treeview."""
        # Xóa bảng cũ nếu có
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Tạo Treeview
        self.tree = ttk.Treeview(self.frame)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Định nghĩa cột
        columns = list(df.columns)
        self.tree["columns"] = columns
        self.tree["show"] = "headings"

        # Tùy chỉnh màu sắc và giao diện Treeview
        style = ttk.Style()
        # Sử dụng chủ đề 'clam' để hỗ trợ đường viền giữa các hàng
        style.theme_use('clam')
        # Tùy chỉnh màu sắc tiêu đề cột
        style.configure("Treeview.Heading", background="#0288D1", foreground="#FFFFFF", font=("Arial", 10, "bold"))
        # Tùy chỉnh màu sắc ô dữ liệu và thêm đường viền
        style.configure("Treeview", rowheight=25, font=("Arial", 10), foreground="#000000", background="#FFFFFF", fieldbackground="#FFFFFF")
        # Tùy chỉnh đường viền giữa các hàng
        style.map("Treeview", background=[('!selected', '#FFFFFF'), ('selected', '#D3D3D3')])
        style.configure("Treeview", bordercolor="#B0BEC5", borderwidth=1)

        # Đặt tiêu đề cột và căn chỉnh
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        # Chèn dữ liệu vào Treeview và tùy chỉnh màu sắc hàng
        for index, row in df.iterrows():
            self.tree.insert("", tk.END, values=list(row), tags=("row",))

        # Tùy chỉnh màu sắc hàng
        self.tree.tag_configure("row", background="#FFFFFF", foreground="#000000")

        # Tùy chỉnh màu sắc tiêu đề hàng (các số 1, 2, 3,...)
        self.tree.tag_configure("tree", background="#0288D1", foreground="#FFFFFF")
        for i, item in enumerate(self.tree.get_children()):
            self.tree.item(item, tags=("row", "tree"))

if __name__ == "__main__":
    root = tk.Tk()
    app = statisticExcel(root)
    root.mainloop()