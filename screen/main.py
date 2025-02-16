import os
import json
from screen.home_teacher_screen import main
from screen.login.login_screen_tc import main_login

config_file = 'login/config.json'

if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        try:
            config_data = json.load(f)
            if config_data:
                main()
            else:
                main_login()
        except json.JSONDecodeError:  # Xử lý khi JSON không hợp lệ
            print("Lỗi: Tệp config không hợp lệ.")
            main_login()
else:
    main_login()
