import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# 你自己的模块按需保留
from config import Config
from routes.auth import auth_bp
from routes.books import books_bp
from routes.borrows import borrows_bp
from models import User


def create_app():
    app = Flask(__name__)

    # 载入配置
    app.config.from_object(Config)

    # 初始化 JWT
    JWTManager(app)

    # 允许跨域（只放行你在 Config.CORS_ORIGINS 里配置的来源）
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(borrows_bp)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify(success=True)

    # （可选）一个简单搜索示例，保留你的逻辑即可
    @app.route("/api/search", methods=["GET"])
    def search_users():
        query = request.args.get("query", "").strip()
        if not query:
            return jsonify(success=False, message="Query parameter required"), 400

        results = User.search(query)
        users = [{"id": r["id"], "username": r["username"], "email": r["email"]} for r in results]
        return jsonify(success=True, data=users)

    return app


# 提供给 Gunicorn / Railway 的 WSGI 入口
app = create_app()


if __name__ == "__main__":
    # 本地运行用，Railway 也可以用，但不如 Gunicorn 稳定
    port = int(os.getenv("PORT", 8080))  # 关键：使用 $PORT（Railway 会注入）
    app.run(host="0.0.0.0", port=port, debug=False)






