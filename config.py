# config.py
import os

class Config:
    """
    通用配置：数据库、密钥、CORS 白名单等
    - 数据库等支持环境变量覆盖
    - CORS_ORIGINS 会自动合并本地开发地址 + 线上前端域名
    """

    # ===== MySQL 配置（按需使用/修改）=====
    MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'SQLPassword')  # 按自己真实密码改
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'webapp')

    # ===== Flask / JWT 密钥 =====
    SECRET_KEY = os.getenv('SECRET_KEY', 'booknest-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'z5M#8uXw6z2r@P!qN7vLsY^fBkJ9eRdT0')

    # ===== Debug 开关（默认 False）=====
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # ===== CORS 白名单 =====
    # 在 Railway「后端」环境变量里设置：
    #   CLIENT_URL = https://booknest-capstone-milestone1-production.up.railway.app
    # 或者用 CORS_ORIGINS 自定义多个，逗号分隔
    CLIENT_URL = os.getenv('CLIENT_URL', '').strip()
    EXTRA_ORIGINS = os.getenv('CORS_ORIGINS', '').strip()   # 支持多个，用逗号分隔

    # 构建最终的 CORS 白名单列表
    _origins = []

    # 线上前端域名（如果提供）
    if CLIENT_URL:
        _origins.append(CLIENT_URL.rstrip('/'))

    # 额外域名（若提供多个，用逗号分隔）
    if EXTRA_ORIGINS:
        _origins.extend(
            [o.strip().rstrip('/') for o in EXTRA_ORIGINS.split(',') if o.strip()]
        )

    # 本地开发常见地址，方便调试（如不需要可以删除）
    _origins.extend([
        'http://127.0.0.1:5000',
        'http://localhost:5000',
    ])

    # 去重，保持顺序
    CORS_ORIGINS = list(dict.fromkeys(_origins))

    # 可选：给 CORS 用的扩展配置（若在 app.py 里需要）
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']


