import sys
import os
# 将项目根目录加入 sys.path，使得可以直接导入 database、recognition 等模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from ui import MainWindow

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x600")
    app = MainWindow(root)
    root.mainloop()