import sqlite3
import os

class Database:
    """
    车牌白名单数据库管理类。
    使用 SQLite，数据库文件默认为 v1/vehicles.db。
    提供添加、删除、查询、列出所有车牌的功能。
    """

    def __init__(self, db_path=None):
        """
        初始化数据库连接，如果数据库文件不存在则自动创建。
        :param db_path: 数据库文件路径，默认位于 v1 文件夹下的 vehicles.db
        """
        if db_path is None:
            # 获取当前文件所在目录的父目录（即 v1 目录）
            base_dir = os.path.dirname(os.path.dirname(__file__))
            db_path = os.path.join(base_dir, 'vehicles.db')
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """创建数据表（如果不存在）"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicles (
                    plate TEXT PRIMARY KEY,   -- 车牌号，唯一标识
                    note TEXT                  -- 备注信息（如车主姓名）
                )
            ''')
            conn.commit()

    def add_vehicle(self, plate, note=''):
        """
        添加一个允许通行的车牌。
        :param plate: 车牌号（字符串）
        :param note: 备注（可选）
        :return: True 添加成功，False 如果车牌已存在
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO vehicles (plate, note) VALUES (?, ?)',
                    (plate, note)
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                # 主键冲突，说明车牌已存在
                return False

    def remove_vehicle(self, plate):
        """
        从白名单中删除一个车牌。
        :param plate: 车牌号
        :return: True 删除成功，False 车牌不存在
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM vehicles WHERE plate = ?', (plate,))
            conn.commit()
            return cursor.rowcount > 0

    def check_vehicle(self, plate):
        """
        检查车牌是否在白名单中。
        :param plate: 车牌号
        :return: True 允许通行，False 禁止通行
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM vehicles WHERE plate = ?', (plate,))
            return cursor.fetchone() is not None

    def list_all(self):
        """
        返回所有白名单车牌及其备注的列表。
        :return: 列表，每个元素为 (plate, note)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT plate, note FROM vehicles')
            return cursor.fetchall()