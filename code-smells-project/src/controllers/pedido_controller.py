"""
Controller de Pedido — logica de negocio para criacao e gestao de pedidos.
Side effects (notificacoes) separados em servico dedicado (TR-17).
"""
import logging
from src.models import pedido_model
from src.config.settings import settings

logger = logging.getLogger(__name__)


def criar_pedido(usuario_id, itens, notification_service=None):
    """Cria pedido com validacao de itens.
    Notificacoes sao disparadas via servico injetado (TR-17)."""
    # Validacao basica de entrada
    if not itens or len(itens) == 0:
        return None, ["Pedido deve ter pelo menos 1 item"]

    resultado = pedido_model.create(usuario_id, itens)

    if "erro" in resultado:
        return None, [resultado["erro"]]

    # Side effects separados — nao bloqueiam o fluxo principal (TR-17)
    if notification_service:
        try:
            notification_service.notify_new_order(
                pedido_id=resultado["pedido_id"],
                usuario_id=usuario_id,
            )
        except Exception:
            logger.warning("Falha ao enviar notificacoes (nao-critico)", exc_info=True)

    return resultado, None


def listar_pedidos_usuario(usuario_id):
    """Lista pedidos de um usuario."""
    pedidos = pedido_model.find_by_usuario(usuario_id)
    return pedidos, None


def listar_todos_pedidos():
    """Lista todos os pedidos."""
    pedidos = pedido_model.find_all()
    return pedidos, None


def atualizar_status_pedido(pedido_id, novo_status, notification_service=None):
    """Atualiza status do pedido com notificacoes condicionais (TR-17)."""
    if novo_status not in settings.STATUS_PEDIDO_VALIDOS:
        return None, [f"Status invalido. Validos: {settings.STATUS_PEDIDO_VALIDOS}"]

    pedido_model.update_status(pedido_id, novo_status)

    # Notificacoes condicionais — nao bloqueiam
    if notification_service:
        try:
            if novo_status == "aprovado":
                notification_service.notify_status_change(
                    pedido_id, "aprovado", "Preparar envio."
                )
            elif novo_status == "cancelado":
                notification_service.notify_status_change(
                    pedido_id, "cancelado", "Devolver estoque."
                )
        except Exception:
            logger.warning("Falha ao enviar notificacao de status", exc_info=True)

    return {"mensagem": "Status atualizado"}, None


def relatorio_vendas():
    """Gera relatorio de vendas agregado."""
    relatorio = pedido_model.get_relatorio_vendas()
    return relatorio, None
