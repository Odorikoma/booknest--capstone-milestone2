# config.py
import os

class Config:
    """
    通用配置：数据库、密钥、CORS 白名单等
    - 支持 Railway MySQL 插件提供的环境变量 (MYSQLHOST/MYSQLPORT/...)
    - 也兼容你自己设置的 MYSQL_HOST/MYSQL_PORT/... 变量
    - CORS 会自动合并前端域名 + 你手动补充的域名 + 本地地址
    """

    # ===== MySQL 配置（优先用 Railway 插件变量）=====
    MYSQL_HOST = (
        os.getenv("MYSQLHOST")           # Railway 插件
        or os.getenv("MYSQL_HOST", "127.0.0.1")
    )
    MYSQL_PORT = int(
        os.getenv("MYSQLPORT")           # Railway 插件
        or os.getenv("MYSQL_PORT", "3306")
    )
    MYSQL_USER = (
        os.getenv("MYSQLUSER")           # Railway 插件
        or os.getenv("MYSQL_USER", "root")
    )
    MYSQL_PASSWORD = (
        os.getenv("MYSQLPASSWORD")       # Railway 插件
        or os.getenv("MYSQL_PASSWORD", "SQLPassword")
    )
    MYSQL_DATABASE = (
        os.getenv("MYSQLDATABASE")       # Railway 插件
        or os.getenv("MYSQL_DATABASE", "webapp")
    )

    # ===== Flask / JWT 密钥 =====
    SECRET_KEY = os.getenv("SECRET_KEY", "booknest-secret-key")
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "z5M#8uXw6zrQP!qN7vLsY^fBkJ9eRdT0"  # 可以换成你自己的
    )

    # ===== Debug 开关（默认为 False）=====
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # ===== CORS 白名单 =====
    # 前端域名（强烈建议在 Railway 后端服务里设置同名变量覆盖）
    CLIENT_URL = os.getenv(
        "CLIENT_URL",
        "https://booknest-app.up.railway.app"  # 你当前的前端域名
    ).strip().rstrip("/")

    # 额外白名单（可逗号分隔多个）
    EXTRA_ORIGINS = os.getenv("CORS_ORIGINS", "").strip()

    # 构建最终白名单
    _origins = []

    # 线上前端域名
    if CLIENT_URL:
        _origins.append(CLIENT_URL)

    # 额外域名（逗号分隔）
    if EXTRA_ORIGINS:
        _origins.extend(
            [o.strip().rstrip("/") for o in EXTRA_ORIGINS.split(",") if o.strip()]
        )

    # 本地常见地址（如不需要可以删掉）
    _origins.extend([
        "http://127.0.0.1:5000",
        "http://localhost:5000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ])

    # 规范化：如果有人只填了裸域名，自动补 http/https 两种前缀
    _norm = []
    seen = set()
    for o in _origins:
        if not o:
            continue
        if o.startswith("http://") or o.startswith("https://"):
            cand = [o]
        else:
            cand = [f"https://{o}", f"http://{o}"]
        for c in cand:
            if c not in seen:
                _norm.append(c)
                seen.add(c)

    # 去重并保序
    CORS_ORIGINS = _norm

    # CORS 其它可选项
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
    CORS_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]




