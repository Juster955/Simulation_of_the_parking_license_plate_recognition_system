from db_manager import Database

def main():
    db = Database()
    print("数据库路径:", db.db_path)

    # 添加测试数据
    db.add_vehicle('京A12345', '测试车1')
    db.add_vehicle('沪B88888', '测试车2')

    # 检查
    print("京A12345 存在?", db.check_vehicle('京A12345'))  # True
    print("粤C99999 存在?", db.check_vehicle('粤C99999'))  # False

    # 列出所有
    print("所有车辆:", db.list_all())

    # 删除测试
    db.remove_vehicle('京A12345')
    print("删除后:", db.list_all())

if __name__ == '__main__':
    main()