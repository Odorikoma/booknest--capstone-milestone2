# config.py
import os

class Config:
    # ===== MySQL 配置（优先用 Railway 插件变量）=====
    MYSQL_HOST = (
        os.getenv("MYSQLHOST")           # Railway 插件
        or os.getenv("MYSQL_HOST", "mainline.proxy.rlwy.net:46348")
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
        or os.getenv("MYSQL_PASSWORD", "EaJFEBqYtzGBymJOJGXGsyyZRpvobgca")
    )
    MYSQL_DATABASE = (
        os.getenv("MYSQLDATABASE")       # Railway 插件
        or os.getenv("MYSQL_DATABASE", "booknest")
    )

    # ===== Flask / JWT 密钥 =====
    SECRET_KEY = os.getenv("SECRET_KEY", "booknest-secret-key")
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "z5M#8uXw6zrQP!qN7vLsY^fBkJ9eRdT0"
    )
    
    # ===== JWT 配置 =====
    JWT_ACCESS_TOKEN_EXPIRES = False
    JWT_ALGORITHM = "HS256"

    # ===== Debug 开关（默认为 False）=====
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # ===== CORS 配置 =====
    # 允许所有来源访问
    CORS_ORIGINS = "*"

    # CORS 其它可选项
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]
    CORS_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]




