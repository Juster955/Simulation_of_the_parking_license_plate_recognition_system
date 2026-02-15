import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import threading
from database import Database
from recognition import EasyOCRPlateRecognizer
from .manage_window import ManageWindow   # 同包内使用相对导入

class MainWindow:
    """主窗口：显示摄像头画面、实时识别结果和通行状态，提供打开管理窗口的按钮。"""

    def __init__(self, root):
        self.root = root
        self.root.title("车牌识别系统 v1")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # 初始化识别器和数据库
        self.recognizer = EasyOCRPlateRecognizer(gpu=False)
        self.db = Database()

        # 打开摄像头
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("错误", "无法打开摄像头")
            self.root.destroy()
            return

        # 创建界面组件
        self.create_widgets()

        # 当前识别结果
        self.current_plate = None
        self.current_conf = 0.0
        self.allowed = False

        # 启动视频更新循环
        self.update_video()

    def create_widgets(self):
        """布局主窗口"""
        # 左侧：视频显示区域
        self.video_label = tk.Label(self.root, bg='black')
        self.video_label.grid(row=0, column=0, rowspan=4, padx=5, pady=5)

        # 右侧：信息面板
        info_frame = tk.Frame(self.root)
        info_frame.grid(row=0, column=1, sticky='n', padx=5, pady=5)

        tk.Label(info_frame, text="识别结果:", font=('Arial', 12)).grid(row=0, column=0, sticky='w')
        self.plate_var = tk.StringVar(value="无")
        tk.Label(info_frame, textvariable=self.plate_var, font=('Arial', 14, 'bold'), fg='blue').grid(row=1, column=0, pady=5)

        tk.Label(info_frame, text="置信度:", font=('Arial', 12)).grid(row=2, column=0, sticky='w')
        self.conf_var = tk.StringVar(value="0.00")
        tk.Label(info_frame, textvariable=self.conf_var).grid(row=3, column=0, pady=5)

        tk.Label(info_frame, text="通行状态:", font=('Arial', 12)).grid(row=4, column=0, sticky='w')
        self.status_var = tk.StringVar(value="等待识别")
        self.status_label = tk.Label(info_frame, textvariable=self.status_var, font=('Arial', 14, 'bold'), fg='orange')
        self.status_label.grid(row=5, column=0, pady=5)

        # 按钮
        btn_frame = tk.Frame(info_frame)
        btn_frame.grid(row=6, column=0, pady=20)

        self.manage_btn = tk.Button(btn_frame, text="管理车牌", command=self.open_manage_window, width=15)
        self.manage_btn.pack(pady=5)

        self.exit_btn = tk.Button(btn_frame, text="退出", command=self.on_close, width=15)
        self.exit_btn.pack(pady=5)

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            small = cv2.resize(frame, (640, 480))
            plates = self.recognizer.recognize(small)
            if plates:
                self.current_plate, self.current_conf = plates[0]
                # ---------- 新增打印 ----------
                print(f"识别到车牌: {self.current_plate}, 置信度: {self.current_conf:.2f}")
                # -------------------------------
                self.plate_var.set(self.current_plate)
                self.conf_var.set(f"{self.current_conf:.2f}")
                self.allowed = self.db.check_vehicle(self.current_plate)
                # ---------- 新增打印 ----------
                print(f"通行状态: {'允许' if self.allowed else '禁止'}")
                # -------------------------------
                # ... 更新状态标签颜色等 ...
            try:
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img_rgb)
                imgtk = ImageTk.PhotoImage(image=img_pil)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
                #print("图像显示更新成功")  # 调试
            except Exception as e:
                print(f"图像显示出错: {e}")
        else:
            print("摄像头读取失败")
        self.root.after(100, self.update_video)


    def open_manage_window(self):
        """打开管理窗口（避免重复打开）"""
        if hasattr(self, 'manage_win') and self.manage_win.winfo_exists():
            self.manage_win.lift()
            return
        from .manage_window import ManageWindow
        self.manage_win = tk.Toplevel(self.root)
        self.manage_win.title("车牌管理")
        # 传递数据库实例，管理窗口将直接操作同一个数据库
        ManageWindow(self.manage_win, self.db)

    def on_close(self):
        """关闭程序时释放摄像头资源"""
        if self.cap.isOpened():
            self.cap.release()
        self.root.destroy()