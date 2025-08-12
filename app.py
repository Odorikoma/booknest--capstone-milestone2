# app.py  —— 完整可直接粘贴版
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from models import User  # 你的项目里已经有的
# 这三个蓝图来自你现有的 routes/ 目录
from routes.auth import auth_bp
from routes.books import books_bp
from routes.borrows import borrows_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # 让 Flask 在代理（Railway）后正确获取 scheme/host
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    # ====== JWT ======
    jwt = JWTManager(app)

    # ====== CORS（关键：对所有路由生效）======
    # 前端域名（不要带结尾的 /）
    client_url = os.getenv("CLIENT_URL", "").rstrip("/")
    # 额外允许的来源（逗号分隔，可选）
    extra_origins = os.getenv("CORS_ORIGINS", "")
    extra_list = [x.strip().rstrip("/") for x in extra_origins.split(",") if x.strip()]

    # 常用本地调试来源也放进去，避免本地调试再改代码
    allowed_origins = [x for x in [client_url, "http://127.0.0.1:5500", "http://localhost:5500"] if x]
    allowed_origins.extend(extra_list)

    # 对所有路径生效，避免因为路径匹配不到而没有加上 CORS 头
    CORS(
        app,
        resources={r"/*": {"origins": allowed_origins}},
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=False,  # 目前不需要 Cookie 时建议为 False
    )

    # ====== 注册蓝图（保持你项目原有的前缀写法）======
    # 注意：这里**不额外加 url_prefix**，与你现有 routes 内的路由保持一致
    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(borrows_bp)

    # ====== 健康检查（前端排错也方便）======
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify(success=True, message="API is healthy"), 200

    # 根路径给个提示，避免前端误请求根地址导致解析 HTML 报错
    @app.route("/", methods=["GET"])
    def root_hint():
        return jsonify(success=False, message="API endpoint not found"), 404

    # 一个简单示例：按用户名/邮箱搜索（你原来 app.py 里已有 models.User）
    @app.route("/api/search", methods=["GET"])
    def search_users():
        query = request.args.get("query", "").strip()
        if not query:
            return jsonify(success=False, message="Query parameter required"), 400

        # 示例：User.search 需要你在 models 里实现（你之前的代码已用到）
        results = User.search(query)
        users = [{"id": r["id"], "username": r["username"], "email": r["email"]} for r in results]
        return jsonify(success=True, data=users), 200

    # 打印所有路由，部署日志中可见，便于确认 /api/books 是否存在
    print("\nAvailable routes:")
    with app.app_context():
        for rule in app.url_map.iter_rules():
            print(f"{list(rule.methods)} -> {rule}")

    return app


# Railway / 本地启动入口
if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", "5000"))  # Railway 会注入 PORT
    app.run(host="0.0.0.0", port=port, debug=bool(os.getenv("DEBUG", "False") == "True"))





