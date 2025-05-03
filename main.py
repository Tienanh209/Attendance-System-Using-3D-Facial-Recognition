from screen.login.login_screen import LoginWindow
from tkinter import Tk

def main():
    root = Tk()
    LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()