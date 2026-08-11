"""
Model de Pedido — acesso a dados de pedidos e itens.
Resolve N+1 queries com batch fetching (TR-09).
"""
import logging
from src.models.database import get_db

logger = logging.getLogger(__name__)


def _pedido_to_dict(row):
    """Serializacao base de pedido."""
    return {
        "id": row["id"],
        "usuario_id": row["usuario_id"],
        "status": row["status"],
        "total": row["total"],
        "criado_em": row["criado_em"],
    }


def _buscar_itens_pedidos(pedido_ids, db):
    """Busca itens de multiplos pedidos em batch — evita N+1 (TR-09).
    Faz 1 query para itens + 1 query para produtos = 2 queries totais."""
    if not pedido_ids:
        return {}

    cursor = db.cursor()

    # 1 query: todos os itens dos pedidos de uma vez
    placeholders = ",".join(["?" for _ in pedido_ids])
    cursor.execute(
        f"SELECT * FROM itens_pedido WHERE pedido_id IN ({placeholders})",
        pedido_ids,
    )
    itens = cursor.fetchall()

    # Coleta todos os produto_ids unicos
    produto_ids = list(set(item["produto_id"] for item in itens))
    produtos_map = {}
    if produto_ids:
        produto_placeholders = ",".join(["?" for _ in produto_ids])
        cursor.execute(
            f"SELECT id, nome FROM produtos WHERE id IN ({produto_placeholders})",
            produto_ids,
        )
        produtos_map = {p["id"]: p["nome"] for p in cursor.fetchall()}

    # Agrupa itens por pedido_id
    itens_por_pedido = {}
    for item in itens:
        itens_por_pedido.setdefault(item["pedido_id"], []).append({
            "produto_id": item["produto_id"],
            "produto_nome": produtos_map.get(item["produto_id"], "Desconhecido"),
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
        })

    return itens_por_pedido


def create(usuario_id, itens):
    """Cria pedido com itens em transacao — queries parametrizadas."""
    db = get_db()
    cursor = db.cursor()

    # Calcula total e valida itens
    total = 0.0
    for item in itens:
        produto_id = item.get("produto_id")
        quantidade = item.get("quantidade", 1)

        if quantidade <= 0:
            return {"erro": "Quantidade deve ser positiva"}

        cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        produto = cursor.fetchone()
        if produto is None:
            return {"erro": f"Produto {produto_id} nao encontrado"}
        if produto["estoque"] < quantidade:
            return {"erro": f"Estoque insuficiente para {produto['nome']}"}

        total += produto["preco"] * quantidade

    # Cria pedido
    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, round(total, 2)),
    )
    pedido_id = cursor.lastrowid

    # Cria itens e atualiza estoque
    for item in itens:
        produto_id = item.get("produto_id")
        quantidade = item.get("quantidade", 1)

        # Busca preco unitario
        cursor.execute("SELECT preco FROM produtos WHERE id = ?", (produto_id,))
        produto = cursor.fetchone()

        cursor.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
            "VALUES (?, ?, ?, ?)",
            (pedido_id, produto_id, quantidade, produto["preco"]),
        )
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (quantidade, produto_id),
        )

    db.commit()
    logger.info("Pedido criado: ID=%d, usuario=%d, total=%.2f", pedido_id, usuario_id, total)
    return {"pedido_id": pedido_id, "total": round(total, 2)}


def find_by_usuario(usuario_id):
    """Busca pedidos de um usuario com itens — sem N+1 (TR-09)."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM pedidos WHERE usuario_id = ? ORDER BY criado_em DESC",
        (usuario_id,),
    )
    pedidos = cursor.fetchall()
    if not pedidos:
        return []

    pedido_ids = [p["id"] for p in pedidos]
    itens_por_pedido = _buscar_itens_pedidos(pedido_ids, db)

    result = []
    for pedido in pedidos:
        pedido_dict = _pedido_to_dict(pedido)
        pedido_dict["itens"] = itens_por_pedido.get(pedido["id"], [])
        result.append(pedido_dict)

    return result


def find_all():
    """Busca todos os pedidos com itens — sem N+1 (TR-09)."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM pedidos ORDER BY criado_em DESC")
    pedidos = cursor.fetchall()
    if not pedidos:
        return []

    pedido_ids = [p["id"] for p in pedidos]
    itens_por_pedido = _buscar_itens_pedidos(pedido_ids, db)

    result = []
    for pedido in pedidos:
        pedido_dict = _pedido_to_dict(pedido)
        pedido_dict["itens"] = itens_por_pedido.get(pedido["id"], [])
        result.append(pedido_dict)

    return result


def update_status(pedido_id, novo_status):
    """Atualiza status do pedido — query parametrizada."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id),
    )
    db.commit()
    logger.info("Status pedido %d alterado para '%s'", pedido_id, novo_status)
    return True


def get_relatorio_vendas():
    """Gera relatorio de vendas com metricas agregadas."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM pedidos")
    total_pedidos = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos")
    faturamento = cursor.fetchone()[0]

    status_counts = {}
    for status in ["pendente", "aprovado", "enviado", "entregue", "cancelado"]:
        cursor.execute(
            "SELECT COUNT(*) FROM pedidos WHERE status = ?", (status,)
        )
        status_counts[status] = cursor.fetchone()[0]

    # Descontos aplicados via tabela de faixas (extraida para config)
    from src.config.settings import settings

    desconto = 0.0
    for limite, taxa in settings.FAIXAS_DESCONTO:
        if faturamento > limite:
            desconto = faturamento * taxa
            break

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": status_counts["pendente"],
        "pedidos_aprovados": status_counts["aprovado"],
        "pedidos_enviados": status_counts["enviado"],
        "pedidos_entregues": status_counts["entregue"],
        "pedidos_cancelados": status_counts["cancelado"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
