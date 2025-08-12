# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

from config import Config
from models import User

# 导入蓝图
from routes.auth import auth_bp
from routes.books import books_bp
from routes.borrows import borrows_bp


def create_app():
    app = Flask(__name__)
    # 载入配置
    app.config.from_object(Config)

    # 初始化 JWT 管理器
    jwt = JWTManager(app)

    # ===== CORS（注册蓝图之前）=====
    # 前端域名从环境变量读取；如果没有则使用你的生产前端域名
    CLIENT_URL = os.environ.get(
        "CLIENT_URL",
        "https://booknest-capstone-milestone1-production.up.railway.app",
    )

    CORS(
        app,
        resources={r"/api/*": {"origins": [CLIENT_URL]}},  # 只放行 /api/* 路径
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )
    # ===== CORS 结束 =====

    # 注册蓝图（如果各蓝图内部已经带了 url_prefix，这里就不要再加）
    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(borrows_bp)

    # 健康检查
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify(success=True), 200

    # 用户搜索（GET /api/search?query=xxx）
    @app.route("/api/search", methods=["GET"])
    def search_users():
        query = request.args.get("query", "").strip()
        if not query:
            return jsonify(success=False, message="Query parameter required"), 400

        results = User.search(query)
        users = [
            {"id": r["id"], "username": r["username"], "email": r["email"]}
            for r in results
        ]
        return jsonify(success=True, data=users), 200

    # 兜底：其他路径提示未找到（保持你之前“API endpoint not found”的效果）
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        return jsonify(message="API endpoint not found", success=False), 404

    return app


if __name__ == "__main__":
    app = create_app()

    # 打印可用路由（便于调试）
    print("\nAvailable routes:")
    for rule in app.url_map.iter_rules():
        print(f"{list(rule.methods)} -> {rule}")

    app.run(host="0.0.0.0", port=5000, debug=True)


