import tkinter as tk
from tkinter import messagebox, ttk
from database import Database   # 绝对导入

class ManageWindow:
    """车牌管理窗口：可添加、删除、查看白名单车牌。"""

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
        """从数据库重新加载数据并刷新列表"""
        # 清空现有项
        for item in self.tree.get_children():
            self.tree.delete(item)
        # 获取所有车牌
        vehicles = self.db.list_all()
        for plate, note in vehicles:
            self.tree.insert('', 'end', values=(plate, note))

    def add_vehicle(self):
        """添加新车牌"""
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
        """删除选中的车牌"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的车牌")
            return
        plate = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("确认", f"确定删除车牌 {plate} 吗？"):
            self.db.remove_vehicle(plate)
            self.refresh_list()