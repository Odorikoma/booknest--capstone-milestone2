from flask import Blueprint, request, jsonify
from models import User
from flask_jwt_extended import create_access_token
from passlib.hash import pbkdf2_sha256  # 用于哈希和验证密码

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    """User Registration"""
    try:
        data = request.get_json()

        required_fields = ["username", "email", "password"]
        for field in required_fields:
            if field not in data:
                return jsonify(
                    {"success": False, "message": f"Missing required field: {field}"}
                ), 400

        existing_user = User.find_by_email(data["email"])
        if existing_user:
            return jsonify({"success": False, "message": "Email already registered"}), 400

        # 使用 passlib 生成哈希
        hashed_password = pbkdf2_sha256.hash(data["password"])
        result = User.create(
            username=data["username"],
            email=data["email"],
            password_hash=hashed_password,
            role=data.get("role", "user"),
        )

        if result:
            return jsonify({"success": True, "message": "Registration successful"}), 201
        else:
            return jsonify({"success": False, "message": "Registration failed"}), 500

    except Exception as e:
        return jsonify({"success": False, "message": f"Registration failed: {str(e)}"}), 500


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """User Login"""
    try:
        data = request.get_json()

        required_fields = ["email", "password"]
        for field in required_fields:
            if field not in data:
                return jsonify(
                    {"success": False, "message": f"Missing required field: {field}"}
                ), 400

        user = User.find_by_email(data["email"])
        if not user:
            return jsonify({"success": False, "message": "Incorrect email or password"}), 401

        # ✅ 用 passlib 验证哈希
        if not pbkdf2_sha256.verify(data["password"], user["password_hash"]):
            return jsonify({"success": False, "message": "Incorrect email or password"}), 401

        user_info = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
        }

        access_token = create_access_token(identity=user["id"])
        return jsonify({
            "success": True,
            "data": user_info,
            "access_token": access_token,
            "message": "Login successful"
        })

    except Exception as e:
        return jsonify({"success": False, "message": f"Login failed: {str(e)}"}), 500

