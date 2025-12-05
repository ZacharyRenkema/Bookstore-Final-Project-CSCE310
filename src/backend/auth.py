from flask import Blueprint, request, jsonify
from models import db, User
from app import bcrypt
import config
import jwt
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)


def generate_token(user: User):
    payload = {
        "sub": user.id,
        "username": user.username,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=8),
    }
    return jwt.encode(payload, config.JWT, algorithm="HS256")


@auth_bp.route("/register", methods=["POST"])
def register():
    # Retrieve data from registration page
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "customer")

    if not username or not email or not password:
        return jsonify({"error": "Missing Required Fields"}), 400

    # TODO: Query for an existing username or email to ensure no duplicates

    # TODO: Hash password from input
    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(username=username, email=email, password_hash=pw_hash, role=role)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(user)
    return jsonify({"token": token, "role": user.role, "username": user.username})
