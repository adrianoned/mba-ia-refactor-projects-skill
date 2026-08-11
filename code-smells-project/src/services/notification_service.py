"""
Servico de Notificacao — side effects separados da logica de negocio (TR-17).
Centraliza envio de emails, SMS e push notifications.
"""
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Gerencia notificacoes do sistema.
    Side effects isolados — falhas em notificacoes nao afetam operacoes principais."""

    def notify_new_order(self, pedido_id, usuario_id):
        """Notifica criacao de novo pedido."""
        logger.info("NOTIFICACAO: Pedido %d criado para usuario %d — enviando email", pedido_id, usuario_id)
        logger.info("NOTIFICACAO: SMS enviado — Seu pedido foi recebido!")
        logger.info("NOTIFICACAO: Push notification — Novo pedido recebido pelo sistema")

    def notify_status_change(self, pedido_id, novo_status, acao):
        """Notifica mudanca de status do pedido."""
        logger.info("NOTIFICACAO: Pedido %d foi marcado como '%s' — %s", pedido_id, novo_status, acao)
