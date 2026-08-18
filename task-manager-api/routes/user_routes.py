"""Rotas de Usuario — autenticacao e CRUD.
Validacao de email, senha forte (min. 8 chars), sem exposicao de hash (TR-15)."""
from flask import Blueprint, request, jsonify
from database import db
from models.user import User
from models.task import Task
from config.settings import settings
import logging
import re
import secrets

logger = logging.getLogger(__name__)
user_bp = Blueprint("users", __name__)

_EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@user_bp.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    result = []
    for u in users:
        user_data = u.to_dict()
        user_data["task_count"] = len(u.tasks)
        result.append(user_data)
    return jsonify(result), 200


@user_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = db.session.get(User,user_id)
    if not user:
        return jsonify({"error": "Usuario nao encontrado"}), 404

    data = user.to_dict()
    tasks = Task.query.filter_by(user_id=user_id).all()
    data["tasks"] = [t.to_dict() for t in tasks]
    return jsonify(data), 200


@user_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados invalidos"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not name:
        return jsonify({"error": "Nome e obrigatorio"}), 400
    if not email:
        return jsonify({"error": "Email e obrigatorio"}), 400
    if not password:
        return jsonify({"error": "Senha e obrigatoria"}), 400
    if not _EMAIL_REGEX.match(email):
        return jsonify({"error": "Email invalido"}), 400
    if len(password) < settings.MIN_PASSWORD_LENGTH:
        return jsonify({"error": f"Senha deve ter no minimo {settings.MIN_PASSWORD_LENGTH} caracteres"}), 400
    if role not in settings.VALID_ROLES:
        return jsonify({"error": "Role invalido"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email ja cadastrado"}), 409

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    try:
        db.session.add(user)
        db.session.commit()
        logger.info("Usuario criado: %d - %s", user.id, user.name)
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao criar usuario: %s", e)
        return jsonify({"error": "Erro ao criar usuario"}), 500


@user_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = db.session.get(User,user_id)
    if not user:
        return jsonify({"error": "Usuario nao encontrado"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados invalidos"}), 400

    if "name" in data:
        user.name = data["name"]

    if "email" in data:
        if not _EMAIL_REGEX.match(data["email"]):
            return jsonify({"error": "Email invalido"}), 400
        existing = User.query.filter_by(email=data["email"]).first()
        if existing and existing.id != user_id:
            return jsonify({"error": "Email ja cadastrado"}), 409
        user.email = data["email"]

    if "password" in data:
        if len(data["password"]) < settings.MIN_PASSWORD_LENGTH:
            return jsonify({"error": f"Senha muito curta (min. {settings.MIN_PASSWORD_LENGTH})"}), 400
        user.set_password(data["password"])

    if "role" in data:
        if data["role"] not in settings.VALID_ROLES:
            return jsonify({"error": "Role invalido"}), 400
        user.role = data["role"]

    if "active" in data:
        user.active = data["active"]

    try:
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao atualizar usuario: %s", e)
        return jsonify({"error": "Erro ao atualizar"}), 500


@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = db.session.get(User,user_id)
    if not user:
        return jsonify({"error": "Usuario nao encontrado"}), 404

    # Cascade delete tasks
    tasks = Task.query.filter_by(user_id=user_id).all()
    for t in tasks:
        db.session.delete(t)

    try:
        db.session.delete(user)
        db.session.commit()
        logger.info("Usuario deletado: %d", user_id)
        return jsonify({"message": "Usuario deletado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao deletar usuario: %s", e)
        return jsonify({"error": "Erro ao deletar"}), 500


@user_bp.route("/users/<int:user_id>/tasks", methods=["GET"])
def get_user_tasks(user_id):
    user = db.session.get(User,user_id)
    if not user:
        return jsonify({"error": "Usuario nao encontrado"}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    result = [t.to_dict() for t in tasks]
    return jsonify(result), 200


@user_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados invalidos"}), 400

    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email e senha sao obrigatorios"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Credenciais invalidas"}), 401

    if not user.check_password(password):
        return jsonify({"error": "Credenciais invalidas"}), 401

    if not user.active:
        return jsonify({"error": "Usuario inativo"}), 403

    # Token seguro com secrets (TR-18)
    token = secrets.token_hex(32)
    logger.info("Login: %s", email)
    return jsonify({
        "message": "Login realizado com sucesso",
        "user": user.to_dict(),
        "token": token,
    }), 200
