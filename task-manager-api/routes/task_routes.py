"""Rotas de Task — apenas roteamento, delegando ao model.
Usa Task.is_overdue() centralizado (TR-10), logging estruturado (TR-14),
tratamento de erros com rollback (TR-12)."""
from flask import Blueprint, request, jsonify
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from datetime import datetime
from config.settings import settings
import logging

logger = logging.getLogger(__name__)
task_bp = Blueprint("tasks", __name__)


def _build_task_response(task):
    """Helper unico para montar resposta de task — usa to_dict() do model."""
    return task.to_dict()


@task_bp.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    result = [_build_task_response(t) for t in tasks]
    return jsonify(result), 200


@task_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = db.session.get(Task,task_id)
    if task:
        return jsonify(task.to_dict()), 200
    return jsonify({"error": "Task nao encontrada"}), 404


@task_bp.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados invalidos"}), 400

    title = data.get("title")
    if not title:
        return jsonify({"error": "Titulo e obrigatorio"}), 400
    if len(title) < settings.MIN_TITLE_LENGTH:
        return jsonify({"error": "Titulo muito curto"}), 400
    if len(title) > settings.MAX_TITLE_LENGTH:
        return jsonify({"error": "Titulo muito longo"}), 400

    status = data.get("status", "pending")
    if status not in settings.VALID_STATUSES:
        return jsonify({"error": "Status invalido"}), 400

    priority = data.get("priority", settings.DEFAULT_PRIORITY)
    if priority not in settings.VALID_PRIORITIES:
        return jsonify({"error": "Prioridade deve ser entre 1 e 5"}), 400

    user_id = data.get("user_id")
    if user_id:
        user = db.session.get(User,user_id)
        if not user:
            return jsonify({"error": "Usuario nao encontrado"}), 404

    category_id = data.get("category_id")
    if category_id:
        cat = db.session.get(Category,category_id)
        if not cat:
            return jsonify({"error": "Categoria nao encontrada"}), 404

    task = Task()
    task.title = title
    task.description = data.get("description", "")
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    due_date = data.get("due_date")
    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, "%Y-%m-%d")
        except (ValueError, TypeError):
            return jsonify({"error": "Formato de data invalido. Use YYYY-MM-DD"}), 400

    tags = data.get("tags")
    if tags:
        task.tags = ",".join(tags) if isinstance(tags, list) else tags

    try:
        db.session.add(task)
        db.session.commit()
        logger.info("Task criada: %d - %s", task.id, task.title)
        return jsonify(task.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao criar task: %s", e)
        return jsonify({"error": "Erro ao criar task"}), 500


@task_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = db.session.get(Task,task_id)
    if not task:
        return jsonify({"error": "Task nao encontrada"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados invalidos"}), 400

    if "title" in data:
        if len(data["title"]) < settings.MIN_TITLE_LENGTH:
            return jsonify({"error": "Titulo muito curto"}), 400
        if len(data["title"]) > settings.MAX_TITLE_LENGTH:
            return jsonify({"error": "Titulo muito longo"}), 400
        task.title = data["title"]

    if "description" in data:
        task.description = data["description"]

    if "status" in data:
        if not task.validate_status(data["status"]):
            return jsonify({"error": "Status invalido"}), 400
        task.status = data["status"]

    if "priority" in data:
        if not task.validate_priority(data["priority"]):
            return jsonify({"error": "Prioridade deve ser entre 1 e 5"}), 400
        task.priority = data["priority"]

    if "user_id" in data:
        if data["user_id"]:
            user = db.session.get(User,data["user_id"])
            if not user:
                return jsonify({"error": "Usuario nao encontrado"}), 404
        task.user_id = data["user_id"]

    if "category_id" in data:
        if data["category_id"]:
            cat = db.session.get(Category,data["category_id"])
            if not cat:
                return jsonify({"error": "Categoria nao encontrada"}), 404
        task.category_id = data["category_id"]

    if "due_date" in data:
        if data["due_date"]:
            try:
                task.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d")
            except (ValueError, TypeError):
                return jsonify({"error": "Formato de data invalido"}), 400
        else:
            task.due_date = None

    if "tags" in data:
        tags = data["tags"]
        task.tags = ",".join(tags) if isinstance(tags, list) else tags

    try:
        db.session.commit()
        logger.info("Task atualizada: %d", task.id)
        return jsonify(task.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao atualizar task: %s", e)
        return jsonify({"error": "Erro ao atualizar"}), 500


@task_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = db.session.get(Task,task_id)
    if not task:
        return jsonify({"error": "Task nao encontrada"}), 404

    try:
        db.session.delete(task)
        db.session.commit()
        logger.info("Task deletada: %d", task_id)
        return jsonify({"message": "Task deletada com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao deletar task: %s", e)
        return jsonify({"error": "Erro ao deletar"}), 500


@task_bp.route("/tasks/search", methods=["GET"])
def search_tasks():
    query = request.args.get("q", "")
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    user_id = request.args.get("user_id", "")

    tasks = Task.query
    if query:
        tasks = tasks.filter(
            db.or_(
                Task.title.like(f"%{query}%"),
                Task.description.like(f"%{query}%"),
            )
        )
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        tasks = tasks.filter(Task.priority == int(priority))
    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))

    results = tasks.all()
    return jsonify([t.to_dict() for t in results]), 200


@task_bp.route("/tasks/stats", methods=["GET"])
def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status="pending").count()
    in_progress = Task.query.filter_by(status="in_progress").count()
    done = Task.query.filter_by(status="done").count()
    cancelled = Task.query.filter_by(status="cancelled").count()

    # overdue via metodo do model (TR-10)
    all_tasks = Task.query.all()
    overdue_count = sum(1 for t in all_tasks if t.is_overdue())

    stats = {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "done": done,
        "cancelled": cancelled,
        "overdue": overdue_count,
        "completion_rate": round((done / total) * 100, 2) if total > 0 else 0,
    }
    return jsonify(stats), 200
