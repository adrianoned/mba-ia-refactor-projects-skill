"""Rotas de Categoria — blueprint proprio (TR-17)."""
from flask import Blueprint, request, jsonify
from database import db
from models.category import Category
from models.task import Task
import logging

logger = logging.getLogger(__name__)
category_bp = Blueprint("categories", __name__)


@category_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    result = []
    for c in categories:
        cat_data = c.to_dict()
        cat_data["task_count"] = Task.query.filter_by(category_id=c.id).count()
        result.append(cat_data)
    return jsonify(result), 200


@category_bp.route("/categories", methods=["POST"])
def create_category():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados invalidos"}), 400

    name = data.get("name")
    if not name:
        return jsonify({"error": "Nome e obrigatorio"}), 400

    category = Category()
    category.name = name
    category.description = data.get("description", "")
    category.color = data.get("color", "#000000")

    try:
        db.session.add(category)
        db.session.commit()
        logger.info("Categoria criada: %d - %s", category.id, category.name)
        return jsonify(category.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao criar categoria: %s", e)
        return jsonify({"error": "Erro ao criar categoria"}), 500


@category_bp.route("/categories/<int:cat_id>", methods=["PUT"])
def update_category(cat_id):
    cat = db.session.get(Category,cat_id)
    if not cat:
        return jsonify({"error": "Categoria nao encontrada"}), 404

    data = request.get_json()
    if "name" in data:
        cat.name = data["name"]
    if "description" in data:
        cat.description = data["description"]
    if "color" in data:
        cat.color = data["color"]

    try:
        db.session.commit()
        return jsonify(cat.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao atualizar categoria: %s", e)
        return jsonify({"error": "Erro ao atualizar"}), 500


@category_bp.route("/categories/<int:cat_id>", methods=["DELETE"])
def delete_category(cat_id):
    cat = db.session.get(Category,cat_id)
    if not cat:
        return jsonify({"error": "Categoria nao encontrada"}), 404

    try:
        db.session.delete(cat)
        db.session.commit()
        logger.info("Categoria deletada: %d", cat_id)
        return jsonify({"message": "Categoria deletada"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao deletar categoria: %s", e)
        return jsonify({"error": "Erro ao deletar"}), 500
