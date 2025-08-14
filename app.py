# app.py
import os
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import User
from routes.auth import auth_bp
from routes.books import books_bp
from routes.borrows import borrows_bp


def create_app() -> Flask:
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)

    # 初始化 JWT 管理器
    jwt = JWTManager(app)

    # 允许前端域名跨域（在 Config.CORS_ORIGINS 里配置了生产前端域名即可）
    cors_origins = getattr(Config, "CORS_ORIGINS", ["*"])
    CORS(app, origins=cors_origins, supports_credentials=True)

    # -----------------------------
    # 注册蓝图
    # 说明：你的蓝图文件里如果路由已经写成 /api/xxx（例如 /api/books），
    # 就用下面这三行（不再加 url_prefix），避免出现 /api/api/... 的问题。
    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(borrows_bp)

    # 如果你的蓝图里是 /books、/auth 这种**不带 /api** 的路径，
    # 请把上面三行替换为下面三行（带 url_prefix）：
    # app.register_blueprint(auth_bp,    url_prefix="/api")
    # app.register_blueprint(books_bp,   url_prefix="/api")
    # app.register_blueprint(borrows_bp, url_prefix="/api")
    # -----------------------------

    @app.get("/api/health")
    def health():
        return jsonify(success=True, service="booknest-api")

    @app.get("/")
    def root():
        # 访问根路径时给一个友好的 404 JSON
        return jsonify(message="API endpoint not found", success=False), 404

    @app.route('/api/users', methods=['GET'])
    def search_users():
        query = request.args.get('query', '').strip()
        if not query:
            return jsonify(success=False, message="Query parameter required"), 400
        try:
            results = User.search(query)
            users = [{"id": r['id'], "username": r['username'], "email": r['email']} for r in results]
            return jsonify(success=True, data=users)
        except Exception as e:
            print("User search error:", e)  # <--- 打印异常
            return jsonify(success=False, message=str(e)), 500

    # 捕获所有静态文件请求
    @app.route('/<path:filename>')
    def serve_static(filename):
        """
        访问 /book-detail.html?id=3
        Flask 返回静态文件，并保留 query string
        """
        return send_from_directory(app.static_folder, filename)

        
    return app


# 让 gunicorn 可以直接 import 到 app 对象
app = create_app()

# 启动时把所有路由打到日志里，方便确认真实路径
print("== ROUTES ==")
for rule in app.url_map.iter_rules():
    print(f"{sorted(rule.methods)}  {rule.rule}")
print("== END ROUTES ==")

if __name__ == "__main__":
    # Railway 会注入 PORT；本地没有时默认 8080
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=False)


















