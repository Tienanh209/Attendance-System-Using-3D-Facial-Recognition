import os
import json
from datetime import datetime

filetype = "py"
# directory = r"C:\Users\chaud\cdthong\mobile\ct312hm01-project-dinhthongchau\lib"
directory =  r"C:\Users\Legion 5 Pro 2023\Documents\GitHub\nckh_070225"


def read_dart_files(directory):
    dart_files = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(f".{filetype}"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    dart_files[file_path] = f.read()
    return dart_files

def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def get_unique_filename(base_name):
    # Tạo tên file duy nhất bằng cách thêm số thứ tự nếu file đã tồn tại
    counter = 1
    file_name, file_extension = os.path.splitext(base_name)
    unique_name = base_name
    while os.path.exists(unique_name):
        unique_name = f"{file_name}_{counter}{file_extension}"
        counter += 1
    return unique_name

if __name__ == "__main__":
    # Đường dẫn thư mục lib của bạn
    lib_directory = directory

    # Lấy thời gian hiện tại và định dạng
    current_time = datetime.now().strftime("%Hh%Mm%Ss_%d%m%y")  # Ví dụ: 12h22_270225

    # File JSON đầu ra
    output_json_file = f"{filetype}code_{current_time}.json"

    # Đảm bảo tên file là duy nhất
    output_json_file = get_unique_filename(output_json_file)

    # Đọc và xuất code Dart
    dart_code = read_dart_files(lib_directory)
    save_to_json(dart_code, output_json_file)
    print(f"Đã xuất {len(dart_code)} file {filetype} vào {output_json_file} cùng thư mục")