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
    app = Flask(__name__, static_folder='assets')
    app.config.from_object(Config)

    # 初始化 JWT 管理器
    jwt = JWTManager(app)
    
    # JWT错误处理器
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Token has expired',
            'error_type': 'token_expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Invalid token',
            'error_type': 'invalid_token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Authorization token required',
            'error_type': 'missing_token'
        }), 401

    # 允许所有域名跨域访问
    cors_origins = getattr(Config, "CORS_ORIGINS", "*")
    CORS(app, 
         origins=cors_origins,
         supports_credentials=getattr(Config, "CORS_SUPPORTS_CREDENTIALS", True),
         allow_headers=getattr(Config, "CORS_ALLOW_HEADERS", ["Content-Type", "Authorization"]),
         methods=getattr(Config, "CORS_METHODS", ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]))

    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(borrows_bp)

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
            print("User search error:", e) 
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

app = create_app()

print("== ROUTES ==")
for rule in app.url_map.iter_rules():
    print(f"{sorted(rule.methods)}  {rule.rule}")
print("== END ROUTES ==")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=False)



















