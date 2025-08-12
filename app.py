# app.py
import os
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config

# 你的蓝图（保持原有 import 路径不变）
from routes.auth import auth_bp
from routes.books import books_bp
from routes.borrows import borrows_bp


def create_app() -> Flask:
    """Flask 应用工厂"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ 只放行 config.py 里配置的白名单，并且仅作用在 /api/* 路径下
    CORS(
        app,
        resources={r"/api/*": {"origins": Config.CORS_ORIGINS}},
        supports_credentials=getattr(Config, "CORS_SUPPORTS_CREDENTIALS", True),
        methods=getattr(
            Config, "CORS_METHODS", ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
        ),
        allow_headers=getattr(
            Config, "CORS_ALLOW_HEADERS", ["Content-Type", "Authorization"]
        ),
    )

    # ✅ 统一挂在 /api/* 路径下，便于前端通过一个前缀访问
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(books_bp, url_prefix="/api/books")
    app.register_blueprint(borrows_bp, url_prefix="/api/borrows")

    # 健康检查
    @app.get("/api/health")
    def health():
        return jsonify(success=True, message="OK"), 200

    # 404 统一 JSON
    @app.errorhandler(404)
    def not_found(_):
        return jsonify(success=False, message="API endpoint not found"), 404

    # 500 统一 JSON（不要泄露 traceback）
    @app.errorhandler(500)
    def server_error(_):
        return jsonify(success=False, message="Server error"), 500

    # 调试输出
    if app.config.get("DEBUG", False):
        print("\n[DEBUG] CORS_ORIGINS:", Config.CORS_ORIGINS)

    return app


# 供 gunicorn 导入，也方便本地直接运行
app = create_app()

if __name__ == "__main__":
    # 本地开发用；Railway 上会通过 $PORT 运行
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))




