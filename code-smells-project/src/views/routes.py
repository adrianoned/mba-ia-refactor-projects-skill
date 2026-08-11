"""
Rotas da aplicacao — apenas roteamento HTTP e formatacao de resposta.
NENHUMA logica de negocio aqui — apenas extracao de parametros e delegacao.
Usa Blueprints para organizacao por dominio.
"""
from flask import Blueprint, request, jsonify, current_app
from src.controllers import produto_controller, usuario_controller, pedido_controller
from src.services.notification_service import NotificationService


# --- Blueprints ---
produto_bp = Blueprint("produtos", __name__)
usuario_bp = Blueprint("usuarios", __name__)
pedido_bp = Blueprint("pedidos", __name__)
admin_bp = Blueprint("admin", __name__)
root_bp = Blueprint("root", __name__)


# ============================================================
# Produtos
# ============================================================

@produto_bp.route("/produtos", methods=["GET"])
def listar_produtos():
    dados, erro = produto_controller.listar_produtos()
    if erro:
        return jsonify({"erro": erro[0], "sucesso": False}), 400
    return jsonify({"dados": dados, "sucesso": True}), 200


@produto_bp.route("/produtos/busca", methods=["GET"])
def buscar_produtos():
    termo = request.args.get("q", None)
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)

    if preco_min:
        preco_min = float(preco_min)
    if preco_max:
        preco_max = float(preco_max)

    dados, erro = produto_controller.buscar_produtos(termo, categoria, preco_min, preco_max)
    if erro:
        return jsonify({"erro": erro[0], "sucesso": False}), 400
    return jsonify(dados), 200


@produto_bp.route("/produtos/<int:produto_id>", methods=["GET"])
def buscar_produto(produto_id):
    dados, erro = produto_controller.buscar_produto(produto_id)
    if erro:
        return jsonify({"erro": erro[0], "sucesso": False}), 404
    return jsonify({"dados": dados, "sucesso": True}), 200


@produto_bp.route("/produtos", methods=["POST"])
def criar_produto():
    dados, erro = produto_controller.criar_produto(request.get_json())
    if erro:
        return jsonify({"erro": erro[0], "sucesso": False}), 400
    return jsonify({"dados": dados, "sucesso": True, "mensagem": "Produto criado"}), 201


@produto_bp.route("/produtos/<int:produto_id>", methods=["PUT"])
def atualizar_produto(produto_id):
    dados, erro = produto_controller.atualizar_produto(produto_id, request.get_json())
    if erro:
        return jsonify({"erro": erro[0], "sucesso": False}), 400
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


@produto_bp.route("/produtos/<int:produto_id>", methods=["DELETE"])
def deletar_produto(produto_id):
    dados, erro = produto_controller.deletar_produto(produto_id)
    if erro:
        return jsonify({"erro": erro[0], "sucesso": False}), 404
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


# ============================================================
# Usuarios
# ============================================================

@usuario_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    dados, erro = usuario_controller.listar_usuarios()
    if erro:
        return jsonify({"erro": erro[0], "sucesso": False}), 400
    return jsonify({"dados": dados, "sucesso": True}), 200


@usuario_bp.route("/usuarios/<int:usuario_id>", methods=["GET"])
def buscar_usuario(usuario_id):
    dados, erro = usuario_controller.buscar_usuario(usuario_id)
    if erro:
        return jsonify({"erro": erro[0], "sucesso": False}), 404
    return jsonify({"dados": dados, "sucesso": True}), 200


@usuario_bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    dados, erro = usuario_controller.criar_usuario(request.get_json())
    if erro:
        return jsonify({"erro": erro[0], "sucesso": False}), 400
    return jsonify({"dados": dados, "sucesso": True}), 201


@usuario_bp.route("/login", methods=["POST"])
def login():
    dados, erro = usuario_controller.login(request.get_json())
    if erro:
        return jsonify({"erro": erro[0], "sucesso": False}), 401
    return jsonify({"dados": dados, "sucesso": True, "mensagem": "Login OK"}), 200


# ============================================================
# Pedidos
# ============================================================

@pedido_bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    dados_req = request.get_json()
    usuario_id = dados_req.get("usuario_id")
    itens = dados_req.get("itens", [])

    if not usuario_id:
        return jsonify({"erro": "Usuario ID e obrigatorio", "sucesso": False}), 400

    notification_svc = NotificationService()
    dados, erro = pedido_controller.criar_pedido(usuario_id, itens, notification_svc)
    if erro:
        return jsonify({"erro": erro[0], "sucesso": False}), 400
    return jsonify({
        "dados": dados,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso",
    }), 201


@pedido_bp.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    dados, erro = pedido_controller.listar_todos_pedidos()
    if erro:
        return jsonify({"erro": erro[0], "sucesso": False}), 400
    return jsonify({"dados": dados, "sucesso": True}), 200


@pedido_bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    dados, erro = pedido_controller.listar_pedidos_usuario(usuario_id)
    if erro:
        return jsonify({"erro": erro[0], "sucesso": False}), 400
    return jsonify({"dados": dados, "sucesso": True}), 200


@pedido_bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    novo_status = request.get_json().get("status", "")
    notification_svc = NotificationService()
    dados, erro = pedido_controller.atualizar_status_pedido(
        pedido_id, novo_status, notification_svc
    )
    if erro:
        return jsonify({"erro": erro[0], "sucesso": False}), 400
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200


@pedido_bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    dados, erro = pedido_controller.relatorio_vendas()
    if erro:
        return jsonify({"erro": erro[0], "sucesso": False}), 400
    return jsonify({"dados": dados, "sucesso": True}), 200


# ============================================================
# Admin (apenas operacoes seguras e predefinidas — TR-04)
# ============================================================

@admin_bp.route("/admin/reset-db", methods=["POST"])
def reset_database():
    """Reset seguro do banco — sem SQL arbitrario (TR-04)."""
    from src.models.database import get_db
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM usuarios")
    db.commit()
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Banco de dados resetado via endpoint admin")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


# ============================================================
# Health Check (sem dados sensiveis — TR-15)
# ============================================================

@root_bp.route("/health", methods=["GET"])
def health_check():
    """Health check seguro — nao expoe secret_key, db_path ou debug."""
    from src.models.database import get_db
    import sqlite3
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.execute("SELECT COUNT(*) FROM produtos")
        produtos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        pedidos = cursor.fetchone()[0]

        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": {
                "produtos": produtos,
                "usuarios": usuarios,
                "pedidos": pedidos,
            },
            "versao": "1.0.0",
        }), 200
    except sqlite3.Error as e:
        return jsonify({"status": "error", "mensagem": "Falha na conexao com banco"}), 500


# ============================================================
# Home
# ============================================================

@root_bp.route("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo a API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


# ============================================================
# Registro de Blueprints
# ============================================================

def register_routes(app):
    """Registra todos os blueprints na aplicacao."""
    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(root_bp)
