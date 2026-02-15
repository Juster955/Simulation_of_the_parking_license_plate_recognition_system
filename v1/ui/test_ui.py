import tkinter as tk
from tkinter import messagebox, ttk
import random

# ---------- 模拟数据库（简单字典）----------
class MockDB:
    def __init__(self):
        self.vehicles = {
            '京A12345': '测试车1',
            '沪B88888': '测试车2',
        }

    def check_vehicle(self, plate):
        return plate in self.vehicles

    def add_vehicle(self, plate, note=''):
        if plate in self.vehicles:
            return False
        self.vehicles[plate] = note
        return True

    def remove_vehicle(self, plate):
        if plate not in self.vehicles:
            return False
        del self.vehicles[plate]
        return True

    def list_all(self):
        return list(self.vehicles.items())

# ---------- 模拟识别器 ----------
class MockRecognizer:
    def __init__(self):
        self.index = 0
        self.plates = ['京A12345', '沪B88888', '粤C99999', '苏D45678']
        self.confidences = [0.95, 0.88, 0.76, 0.92]

    def recognize(self, image=None):
        # 循环返回不同的车牌，模拟动态识别
        idx = self.index % len(self.plates)
        self.index += 1
        return [(self.plates[idx], self.confidences[idx])]

# ---------- 主窗口 ----------
class TestMainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("UI 测试 - 主窗口")
        self.root.geometry("800x500")

        self.db = MockDB()
        self.recognizer = MockRecognizer()

        self.create_widgets()
        self.update_display()

    def create_widgets(self):
        # 左侧占位图像（用灰色色块代替摄像头画面）
        self.video_label = tk.Label(self.root, bg='gray', width=60, height=20)
        self.video_label.pack(side='left', padx=10, pady=10)

        # 右侧信息面板
        info_frame = tk.Frame(self.root)
        info_frame.pack(side='right', fill='y', padx=10, pady=10)

        tk.Label(info_frame, text="识别结果:", font=('Arial', 12)).pack(anchor='w')
        self.plate_var = tk.StringVar(value="无")
        tk.Label(info_frame, textvariable=self.plate_var, font=('Arial', 14, 'bold'), fg='blue').pack(anchor='w', pady=5)

        tk.Label(info_frame, text="置信度:", font=('Arial', 12)).pack(anchor='w')
        self.conf_var = tk.StringVar(value="0.00")
        tk.Label(info_frame, textvariable=self.conf_var).pack(anchor='w', pady=5)

        tk.Label(info_frame, text="通行状态:", font=('Arial', 12)).pack(anchor='w')
        self.status_var = tk.StringVar(value="等待识别")
        self.status_label = tk.Label(info_frame, textvariable=self.status_var, font=('Arial', 14, 'bold'), fg='orange')
        self.status_label.pack(anchor='w', pady=5)

        # 按钮
        self.manage_btn = tk.Button(info_frame, text="管理车牌", command=self.open_manage_window, width=15)
        self.manage_btn.pack(pady=10)

        self.exit_btn = tk.Button(info_frame, text="退出", command=self.root.destroy, width=15)
        self.exit_btn.pack()

    def update_display(self):
        """模拟识别过程"""
        plates = self.recognizer.recognize()
        if plates:
            plate, conf = plates[0]
            self.plate_var.set(plate)
            self.conf_var.set(f"{conf:.2f}")
            allowed = self.db.check_vehicle(plate)
            if allowed:
                self.status_var.set("允许通行")
                self.status_label.config(fg='green')
            else:
                self.status_var.set("禁止通行")
                self.status_label.config(fg='red')
        else:
            self.plate_var.set("无")
            self.conf_var.set("0.00")
            self.status_var.set("等待识别")
            self.status_label.config(fg='orange')

        # 每隔 2 秒更新一次
        self.root.after(2000, self.update_display)

    def open_manage_window(self):
        """打开管理窗口"""
        win = tk.Toplevel(self.root)
        win.title("车牌管理 - 测试")
        ManageWindow(win, self.db)

# ---------- 管理窗口 ----------
class ManageWindow:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        # 添加区域
        add_frame = tk.Frame(self.parent)
        add_frame.pack(pady=5)

        tk.Label(add_frame, text="车牌号:").grid(row=0, column=0, padx=5)
        self.entry_plate = tk.Entry(add_frame, width=15)
        self.entry_plate.grid(row=0, column=1, padx=5)

        tk.Label(add_frame, text="备注:").grid(row=0, column=2, padx=5)
        self.entry_note = tk.Entry(add_frame, width=15)
        self.entry_note.grid(row=0, column=3, padx=5)

        self.add_btn = tk.Button(add_frame, text="添加", command=self.add_vehicle)
        self.add_btn.grid(row=0, column=4, padx=5)

        # 列表区域
        list_frame = tk.Frame(self.parent)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('车牌号', '备注')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        self.tree.heading('车牌号', text='车牌号')
        self.tree.heading('备注', text='备注')
        self.tree.column('车牌号', width=120)
        self.tree.column('备注', width=200)
        self.tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

        # 删除和刷新按钮
        btn_frame = tk.Frame(self.parent)
        btn_frame.pack(pady=5)

        self.delete_btn = tk.Button(btn_frame, text="删除选中", command=self.delete_vehicle)
        self.delete_btn.pack(side='left', padx=5)

        self.refresh_btn = tk.Button(btn_frame, text="刷新列表", command=self.refresh_list)
        self.refresh_btn.pack(side='left', padx=5)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        vehicles = self.db.list_all()
        for plate, note in vehicles:
            self.tree.insert('', 'end', values=(plate, note))

    def add_vehicle(self):
        plate = self.entry_plate.get().strip()
        if not plate:
            messagebox.showwarning("警告", "请输入车牌号")
            return
        note = self.entry_note.get().strip()
        if self.db.add_vehicle(plate, note):
            messagebox.showinfo("成功", f"添加 {plate} 成功")
            self.entry_plate.delete(0, 'end')
            self.entry_note.delete(0, 'end')
            self.refresh_list()
        else:
            messagebox.showerror("失败", f"车牌 {plate} 已存在")

    def delete_vehicle(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的车牌")
            return
        plate = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("确认", f"确定删除车牌 {plate} 吗？"):
            self.db.remove_vehicle(plate)
            self.refresh_list()


if __name__ == "__main__":
    root = tk.Tk()
    app = TestMainWindow(root)
    root.mainloop()