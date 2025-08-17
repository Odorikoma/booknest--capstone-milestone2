from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)  # 路由仍走 /api/auth/...

# -------------------------
# Register
# -------------------------
@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""
        role = (data.get("role") or "user").strip() or "user"

        if not username or not email or not password:
            return jsonify({"success": False, "message": "username, email and password are required"}), 400

        if User.find_by_email(email):
            return jsonify({"success": False, "message": "Email already registered"}), 400

        # 生成哈希并按你的表结构写入 password_hash 列
        pwd_hash = generate_password_hash(password)
        result = User.create(
            username=username,
            email=email,
            password_hash=pwd_hash,   # 关键：写入哈希而不是明文
            role=role,
        )

        if result:
            return jsonify({"success": True, "message": "Registration successful"}), 201
        return jsonify({"success": False, "message": "Registration failed"}), 500

    except Exception as e:
        return jsonify({"success": False, "message": f"Registration failed: {str(e)}"}), 500


# -------------------------
# Login
# -------------------------
@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.get_json(silent=True) or {}
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""

        if not email or not password:
            return jsonify({"success": False, "message": "email and password are required"}), 400

        user = User.find_by_email(email)
        if not user:
            return jsonify({"success": False, "message": "Incorrect email or password"}), 401

        # 兼容两种返回：find_by_email 若有 "password"（来自 password_hash AS password）优先用；
        # 否则回退用 "password_hash"
        pwd_hash = user.get("password") or user.get("password_hash")
        if not pwd_hash or not check_password_hash(pwd_hash, password):
            return jsonify({"success": False, "message": "Incorrect email or password"}), 401

        user_info = {
            "id": user.get("id"),
            "username": user.get("username"),
            "email": user.get("email"),
            "role": user.get("role"),
        }

        # 生成JWT token，identity用user id（转换为字符串）
        access_token = create_access_token(identity=str(user["id"]))

        return jsonify({
            "success": True,
            "data": user_info,
            "access_token": access_token,  # 返回token
            "message": "Login successful"
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"Login failed: {str(e)}"}), 500


