# 配置文件
import os

# 基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据库文件路径（相对于本项目）
DB_PATH = os.path.join(BASE_DIR, 'database', 'vehicles.db')

# 识别模块参数（可复用 v1 设置）
RECOGNITION = {
    'gpu': False,          # 如果门卫电脑有 NVIDIA 显卡且安装了 GPU 版 torch，可设为 True
    'lang_list': ['ch_sim', 'en']
}

# 冷却时间（秒）：放行一辆车后暂停识别的时间
COOLDOWN_SECONDS = 10

# Flask 服务配置
FLASK_HOST = '0.0.0.0'      # 监听所有网卡，允许局域网其他设备访问
FLASK_PORT = 5000
FLASK_DEBUG = False          # 生产环境关闭调试模式

# 是否允许跨域（如果树莓派和其他设备需要访问 API，可以开启）
CORS_ENABLED = True