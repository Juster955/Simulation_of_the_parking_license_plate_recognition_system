import sys
import os
import time
import threading
from functools import wraps
from flask import Flask, request, jsonify, render_template, send_from_directory
from datetime import datetime
from collections import deque

# 将当前目录加入 sys.path，以便导入同级模块
sys.path.append(os.path.dirname(__file__))

# 导入配置文件
import config

# 导入识别模块和数据库模块（假设从 v1 复制过来，结构保持不变）
from recognition import EasyOCRPlateRecognizer
from database import Database

# 初始化 Flask 应用
app = Flask(__name__)

# 可选：启用跨域支持（如需局域网访问）
if config.CORS_ENABLED:
    from flask_cors import CORS
    CORS(app)

# 初始化识别器和数据库（全局单例）
recognizer = EasyOCRPlateRecognizer(
    gpu=config.RECOGNITION['gpu'],
    lang_list=config.RECOGNITION['lang_list']
)
db = Database(db_path=config.DB_PATH)

# 冷却控制
last_pass_time = 0
cooldown_lock = threading.Lock()

# 存储最近识别记录（最多保留20条）
recent_records = deque(maxlen=20)

def check_cooldown():
    """检查是否处于冷却期"""
    global last_pass_time
    with cooldown_lock:
        return time.time() - last_pass_time < config.COOLDOWN_SECONDS

def set_pass_time():
    """记录放行时间"""
    global last_pass_time
    with cooldown_lock:
        last_pass_time = time.time()

# ---------- 路由 ----------
@app.route('/')
def index():
    """主页：显示识别结果和简单状态"""
    return render_template('index.html')

@app.route('/manage')
def manage():
    """车牌管理页面"""
    return render_template('manage.html')

@app.route('/api/recognize', methods=['POST'])
def recognize():
    """
    树莓派调用此接口上传图片。
    请求格式：multipart/form-data，字段名为 'image'
    返回 JSON：{"plate": str, "allowed": bool, "message": str, "cooldown": bool}
    """
    if check_cooldown():
        return jsonify({
            'plate': None,
            'allowed': False,
            'message': '系统冷却中，请稍后',
            'cooldown': True
        })

    # 获取上传的图片
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # 读取图片（OpenCV 格式）
    import cv2
    import numpy as np
    img_bytes = file.read()
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({'error': 'Invalid image'}), 400

    # 调用识别模块
    plates = recognizer.recognize(img)
    if not plates:
        return jsonify({
            'plate': None,
            'allowed': False,
            'message': '未识别到车牌',
            'cooldown': False
        })

    plate, confidence = plates[0]  # 取最佳结果
    allowed = db.check_vehicle(plate)

    # 记录本次识别结果
    recent_records.appendleft({
        'plate': plate,
        'confidence': round(confidence, 2),
        'allowed': allowed,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    # 如果允许通行，记录放行时间（进入冷却）
    if allowed:
        set_pass_time()
        # 可选：在此处添加向树莓派发送指令的逻辑，或由树莓派自己决定
        # 例如：通过串口或网络通知闸机抬杆，但这里我们只返回结果

    return jsonify({
        'plate': plate,
        'confidence': round(confidence, 2),
        'allowed': allowed,
        'message': '允许通行' if allowed else '禁止通行',
        'cooldown': False
    })

# ---------- 获取最近记录 API ----------
@app.route('/api/latest', methods=['GET'])
def latest():
    """返回最新一条识别记录"""
    if recent_records:
        return jsonify(recent_records[0])
    else:
        return jsonify(None)

@app.route('/api/recent', methods=['GET'])
def recent():
    """返回最近识别记录，可选参数 limit 控制数量"""
    limit = request.args.get('limit', default=10, type=int)
    return jsonify(list(recent_records)[:limit])

# ---------- 数据库管理 API ----------
@app.route('/api/vehicles', methods=['GET'])
def list_vehicles():
    """列出所有白名单车牌"""
    vehicles = db.list_all()
    return jsonify([{'plate': p, 'note': n} for p, n in vehicles])

@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    """添加车牌，请求 JSON 格式：{"plate": "xxx", "note": "xxx"}"""
    data = request.get_json()
    if not data or 'plate' not in data:
        return jsonify({'error': 'Missing plate'}), 400
    plate = data['plate'].strip()
    note = data.get('note', '').strip()
    success = db.add_vehicle(plate, note)
    if success:
        return jsonify({'message': '添加成功', 'plate': plate})
    else:
        return jsonify({'error': '车牌已存在'}), 409

@app.route('/api/vehicles/<plate>', methods=['DELETE'])
def delete_vehicle(plate):
    """删除车牌"""
    success = db.remove_vehicle(plate)
    if success:
        return jsonify({'message': '删除成功'})
    else:
        return jsonify({'error': '车牌不存在'}), 404

# ---------- 静态文件服务 ----------
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# ---------- 启动 ----------
if __name__ == '__main__':
    # 确保数据库初始化（Database 类已自动创建表）
    print(f"数据库路径: {config.DB_PATH}")
    print(f"冷却时间: {config.COOLDOWN_SECONDS} 秒")
    print(f"启动 Flask 服务: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
        threaded=True
    )